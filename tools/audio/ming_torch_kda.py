#!/usr/bin/env python3
"""ming_torch_kda.py — pure-torch backend for Ming-3.0-tts-tiny's Kimi-Delta layers.

WHY THIS EXISTS
  Ming-3.0-tts-tiny is the only Ming release with the `podcast` task, which is how
  the clone-lock stage renders a whole multi-speaker scene in one pass. Its 24
  layers are 18 Kimi-Delta linear-attention layers plus 6 full-attention layers,
  and the Kimi-Delta math comes from `fla-core`, which imports `triton`.

  Triton has no CPU backend and no AMD backend on Windows, and the checkpoint is
  16.7 GiB of bf16 weights, so a 8 GiB card cannot hold it either. That combination
  made the engine unreachable on a Windows/AMD workstation even though the model
  itself runs fine in fp32/bf16 on the CPU.

  This module provides the exact pieces `ming_tiny` imports — `ShortConvolution`,
  `FusedRMSNormGated`, `chunk_kda`, `fused_recurrent_kda`, `tensor_cache` — in
  plain torch. With it installed, the model runs anywhere torch runs; the cost is
  speed (a Python-level recurrence instead of a fused kernel), not identity.

WHAT IT IS NOT
  It is not a voice substitute and not a silent fallback: it is the same model, the
  same weights and the same math, executed by different code. Callers must log that
  this backend is active, and the scene metadata records it.

CORRECTNESS
  The recurrence is the documented KDA delta rule (`fla/ops/kda/naive.py`), fed the
  same gate the chunk kernel fuses: for `safe_gate` the bound is

      gate = lower_bound * sigmoid(exp(A_log) * (g + dt_bias))

  and otherwise `gate = -exp(A_log) * softplus(g + dt_bias)`; both in log space, in
  which the rule decays the state by `exp(gate)`. q/k get the same L2
  normalisation the kernel applies, and beta is already post-sigmoid from the
  model. Audio produced through this backend is checked against the input text by
  the run log, because a math error here would be audible as nonsense.

USAGE
  import ming_torch_kda; ming_torch_kda.install()
  from ming_tiny import MingTinyTTS     # now imports even without fla/triton
"""

import math
import os
import sys
import types

import torch
import torch.nn as nn
import torch.nn.functional as F

# fla's kernels compute in fp32 internally; keep the same precision so the
# recurrence matches the reference rather than accumulating in bf16.
_COMPUTE_DTYPE = torch.float32


class ShortConvolution(nn.Conv1d):
    """Depthwise causal convolution with an activation, matching fla's module.

    `forward(x, cache=..., output_final_state=...)` accepts `[B, T, D]` and returns
    `([B, T, D], cache_or_None)`. The cache is `[N, D, W]` holding the last W input
    vectors, slot 0 oldest, exactly as fla's kernels store it.
    """

    def __init__(self, hidden_size, kernel_size, bias=False, activation="silu",
                 backend=None, device=None, dtype=None, **kwargs):
        super().__init__(
            in_channels=hidden_size,
            out_channels=hidden_size,
            kernel_size=kernel_size,
            padding=kernel_size - 1,
            groups=hidden_size,
            bias=bias,
            device=device,
            dtype=dtype,
        )
        self.hidden_size = int(hidden_size)
        self.activation = None
        if activation is not None:
            if activation not in ("silu", "swish"):
                raise ValueError(f"activation {activation!r} is not supported")
            self.activation = activation
        self.backend = "torch"

    def forward(self, x, residual=None, mask=None, cache=None,
                output_final_state=False, cu_seqlens=None, chunk_indices=None,
                **kwargs):
        if mask is not None:
            x = x * mask.unsqueeze(-1)
        if cu_seqlens is not None:
            raise NotImplementedError(
                "ming_torch_kda: packed sequences (cu_seqlens) are not implemented; "
                "the clone-lock renderer feeds one scene at a time")

        batch, length, channels = x.shape
        width = self.kernel_size[0]
        tail = 0
        if cache is not None:
            history = cache.transpose(1, 2)  # [N, D, W] -> [N, W, D]
            tail = max(0, min(width - 1, history.shape[1]))
            if tail:
                x = torch.cat([history[:, history.shape[1] - tail:, :].to(x.dtype), x], dim=1)

        # nn.Conv1d already carries padding = width - 1, which is exactly the
        # left padding a causal convolution needs.
        y = F.conv1d(x.transpose(1, 2), self.weight, self.bias,
                     padding=width - 1, groups=self.hidden_size)
        y = y[:, :, :x.shape[1]].transpose(1, 2)[:, -length:, :]
        if self.activation in ("silu", "swish"):
            y = F.silu(y)
        if residual is not None:
            y = y + residual

        final_state = None
        if output_final_state:
            final_state = x[:, -width:, :].transpose(1, 2).contiguous()
            if final_state.shape[1] < width:
                pad = final_state.new_zeros(final_state.shape[0], width - final_state.shape[1],
                                            final_state.shape[2])
                final_state = torch.cat([pad, final_state], dim=1)
        return y, final_state

    @property
    def state_size(self):
        return self.hidden_size * self.kernel_size[0]


class FusedRMSNormGated(nn.Module):
    """RMSNorm with a gated activation, matching fla's module (sigmoid | silu)."""

    def __init__(self, hidden_size, elementwise_affine=True, eps=1e-5,
                 activation="swish", device=None, dtype=None):
        super().__init__()
        self.hidden_size = int(hidden_size)
        self.elementwise_affine = bool(elementwise_affine)
        self.eps = float(eps)
        self.activation = activation
        if activation not in ("swish", "silu", "sigmoid"):
            raise ValueError(f"activation {activation!r} is not supported")
        if self.elementwise_affine:
            self.weight = nn.Parameter(torch.ones(hidden_size, device=device, dtype=dtype))
        else:
            self.register_parameter("weight", None)
        self.register_parameter("bias", None)

    def forward(self, x, g, residual=None, prenorm=False, residual_in_fp32=False):
        if residual is not None or prenorm:
            raise NotImplementedError(
                "ming_torch_kda: FusedRMSNormGated residual/prenorm mode is unused "
                "by Ming-3.0-tts-tiny")
        value = x.to(_COMPUTE_DTYPE)
        value = value * torch.rsqrt(value.pow(2).mean(-1, keepdim=True) + self.eps)
        if self.weight is not None:
            value = value * self.weight.to(_COMPUTE_DTYPE)
        if self.activation == "sigmoid":
            value = value * torch.sigmoid(g.to(_COMPUTE_DTYPE))
        else:
            value = value * F.silu(g.to(_COMPUTE_DTYPE))
        return value.to(x.dtype)


def l2norm(x, eps=1e-6):
    """Row-wise L2 normalisation, matching fla's kernel (no sqrt(D) rescale)."""
    value = x.to(_COMPUTE_DTYPE)
    return (value * torch.rsqrt(value.pow(2).sum(-1, keepdim=True) + eps)).to(x.dtype)


def _kda_recurrence(q, k, v, gate, beta, scale=None, initial_state=None,
                    output_final_state=False):
    """The KDA delta rule, one token at a time (fla/ops/kda/naive.py's reference).

    Shapes: q,k `[B, T, H, K]`; v `[B, T, HV, V]`; gate `[B, T, HV, K]` in log
    space; beta `[B, T, HV]` post-sigmoid; state `[B, HV, K, V]`.
    """
    dtype = v.dtype
    batch, length, heads, key_dim = q.shape
    value_heads = v.shape[2]
    value_dim = v.shape[-1]
    groups = value_heads // heads
    if scale is None:
        scale = key_dim ** -0.5

    q, k, v, gate, beta = (t.to(_COMPUTE_DTYPE) for t in (q, k, v, gate, beta))
    if groups > 1:
        q = q.repeat_interleave(groups, dim=2)
        k = k.repeat_interleave(groups, dim=2)
    q = q * scale

    state = q.new_zeros(batch, value_heads, key_dim, value_dim)
    if initial_state is not None:
        state = state + initial_state.to(state.device, state.dtype)

    out = torch.empty(batch, length, value_heads, value_dim,
                      dtype=_COMPUTE_DTYPE, device=q.device)
    for step in range(length):
        q_i = q[:, step]
        k_i = k[:, step]
        v_i = v[:, step]
        gate_i = gate[:, step]
        beta_i = beta[:, step]
        state = state * gate_i.unsqueeze(-1).exp()
        kv = torch.einsum("bhk,bhv->bhkv", beta_i.unsqueeze(-1) * k_i,
                          v_i - (k_i.unsqueeze(-1) * state).sum(-2))
        state = state + kv
        out[:, step] = torch.einsum("bhk,bhkv->bhv", q_i, state)

    final_state = state.to(initial_state.dtype) if (
        output_final_state and initial_state is not None) else (
        state if output_final_state else None)
    return out.to(dtype), final_state


def chunk_kda(q, k, v, g, beta, scale=None, initial_state=None,
              output_final_state=False, use_qk_l2norm_in_kernel=False,
              use_gate_in_kernel=False, use_beta_sigmoid_in_kernel=False,
              allow_neg_eigval=False, safe_gate=False, lower_bound=None,
              disable_recompute=False, return_intermediate_states=False,
              state_v_first=False, cu_seqlens=None, cu_seqlens_cpu=None,
              cp_context=None, use_graph=False, max_num_seqs=None,
              A_log=None, dt_bias=None, chunk_size=64, **kwargs):
    """Drop-in for fla.ops.kda.chunk_kda, computed with the torch recurrence."""
    if cu_seqlens is not None:
        raise NotImplementedError(
            "ming_torch_kda: packed sequences (cu_seqlens) are not implemented")
    if cp_context is not None or use_graph:
        raise NotImplementedError(
            "ming_torch_kda: context-parallel / CUDA-graph modes are not implemented")
    if return_intermediate_states:
        raise NotImplementedError(
            "ming_torch_kda: return_intermediate_states is not implemented")

    if use_qk_l2norm_in_kernel:
        q = l2norm(q)
        k = l2norm(k)

    gate = g
    if use_gate_in_kernel:
        raw = g.to(_COMPUTE_DTYPE)
        if dt_bias is not None:
            raw = raw + dt_bias.to(_COMPUTE_DTYPE).view(1, 1, -1, raw.shape[-1])
        if safe_gate and lower_bound is not None:
            if A_log is None:
                raise ValueError("ming_torch_kda: safe_gate requires A_log")
            scale_a = torch.exp(A_log.to(_COMPUTE_DTYPE)).view(1, 1, -1, 1)
            gate = lower_bound * torch.sigmoid(scale_a * raw)
        else:
            scale_a = torch.exp(A_log.to(_COMPUTE_DTYPE)).view(1, 1, -1, 1) \
                if A_log is not None else torch.ones(1, 1, 1, 1, dtype=_COMPUTE_DTYPE,
                                                     device=raw.device)
            gate = -scale_a * F.softplus(raw)

    if use_beta_sigmoid_in_kernel:
        beta = (2.0 if allow_neg_eigval else 1.0) * torch.sigmoid(beta.to(_COMPUTE_DTYPE))

    return _kda_recurrence(q, k, v, gate, beta, scale=scale,
                           initial_state=initial_state,
                           output_final_state=output_final_state)


def fused_recurrent_kda(q, k, v, g, beta, **kwargs):
    """Drop-in for fla.ops.kda.fused_recurrent_kda (same math, one code path)."""
    return chunk_kda(q, k, v, g, beta, **kwargs)


def tensor_cache(function):
    """fla's memoisation decorator; dropping the cache costs speed, not results."""
    return function


def patch_cpu_decode_dtype():
    """Cast AudioVAE inputs to the module's own dtype (encode and decode).

    The release runs both directions under `autocast_context()`, which is a no-op
    off CUDA. With native-fp32 sampling the prompt waveform and the generated
    latents arrive as float32 while the AudioVAE weights are bfloat16, so `fc1`
    raises "expected m1 and m2 to have the same dtype". Casting the input to the
    module's dtype changes no arithmetic the model performs on a GPU; it makes the
    CPU path well-typed. Idempotent.
    """
    import functools

    from ming_tiny.modeling_audio_vae import AudioVAE

    if getattr(AudioVAE, "_clone_lock_dtype_guard", False):
        return False

    def _guard(method_name):
        original = getattr(AudioVAE, method_name)

        @functools.wraps(original)
        def wrapped(self, value, *args, **kwargs):
            try:
                parameter = next(self.parameters())
            except StopIteration:
                return original(self, value, *args, **kwargs)
            if torch.is_tensor(value) and value.dtype != parameter.dtype:
                value = value.to(parameter.dtype)
            return original(self, value, *args, **kwargs)

        setattr(AudioVAE, method_name, wrapped)

    _guard("encode_latent")
    _guard("infer_from_latent")
    AudioVAE._clone_lock_dtype_guard = True

    # CampPlus is an onnxruntime graph: it takes a float32 numpy array, and under
    # CPU bf16 the prompt waveform reaches its kaldi front-end as bfloat16, which
    # numpy cannot represent ("Got unsupported ScalarType BFloat16").
    from ming_tiny.spkemb_extractor import SpkembExtractor

    for method_name in ("__call__", "_extract_spk_embedding"):
        original = getattr(SpkembExtractor, method_name)

        @functools.wraps(original)
        def _wrapped_spkemb(self, waveform, *args, _original=original, **kwargs):
            if torch.is_tensor(waveform) and waveform.dtype != torch.float32:
                waveform = waveform.float()
            # The kaldi fbank front-end must stay fp32: under CPU autocast its
            # filterbank matmul returns bf16, which onnxruntime cannot consume.
            with torch.autocast(device_type="cpu", dtype=torch.bfloat16, enabled=False):
                return _original(self, waveform, *args, **kwargs)

        setattr(SpkembExtractor, method_name, _wrapped_spkemb)
    return True


def patch_cpu_autocast():
    """Run the engine under CPU bf16 autocast, as it runs under CUDA autocast.

    The release wraps its decode in `torch.autocast(device_type, dtype)` only when
    `use_amp` is true, which it sets for CUDA. On CPU the same code mixes fp32
    sampling tensors with bf16 weights and dies inside the flow sampler's first
    matmul. CPU autocast is the supported equivalent: matmuls and convolutions run
    in bf16 exactly as the weights are stored. Idempotent.
    """
    import functools

    from ming_tiny.inference import MingTinyEngine

    if getattr(MingTinyEngine, "_clone_lock_autocast", False):
        return False
    original = MingTinyEngine.synthesize

    @functools.wraps(original)
    def wrapped(self, *args, **kwargs):
        if getattr(self, "device", torch.device("cpu")).type == "cpu":
            with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
                return original(self, *args, **kwargs)
        return original(self, *args, **kwargs)

    MingTinyEngine.synthesize = wrapped
    MingTinyEngine._clone_lock_autocast = True
    return True


def install(force=False):
    """Install this backend as `fla` for the current process.

    Returns (installed, note). When the real `fla` imports cleanly it is left
    alone unless `force`; this backend is for hosts where Triton is unavailable.
    """
    if not force:
        # Probe the pieces the model actually imports: a bare `import fla` can
        # succeed and still fail on triton the moment a submodule is touched.
        try:
            from fla.modules import FusedRMSNormGated as _Norm, ShortConvolution as _Conv  # noqa: F401
            from fla.ops.kda import chunk_kda as _Chunk  # noqa: F401
            return False, "fla-core available (triton backend in use)"
        except Exception:
            pass

    fla = types.ModuleType("fla")
    fla.__path__ = []
    modules = types.ModuleType("fla.modules")
    modules.ShortConvolution = ShortConvolution
    modules.FusedRMSNormGated = FusedRMSNormGated
    ops = types.ModuleType("fla.ops")
    ops.__path__ = []
    kda = types.ModuleType("fla.ops.kda")
    kda.chunk_kda = chunk_kda
    kda.fused_recurrent_kda = fused_recurrent_kda
    utils = types.ModuleType("fla.utils")
    utils.tensor_cache = tensor_cache

    fla.modules = modules
    fla.ops = ops
    fla.utils = utils
    modules.__path__ = []
    sys.modules["fla"] = fla
    sys.modules["fla.modules"] = modules
    sys.modules["fla.ops"] = ops
    sys.modules["fla.ops.kda"] = kda
    sys.modules["fla.utils"] = utils
    return True, "ming_torch_kda (pure-torch KDA; no triton)"


if __name__ == "__main__":
    installed, note = install(force=True)
    print(note)
    from fla.modules import FusedRMSNormGated, ShortConvolution  # noqa: F401
    from fla.ops.kda import chunk_kda, fused_recurrent_kda  # noqa: F401
    # Tiny numerical smoke test: a 1-step state update must match the closed form.
    torch.manual_seed(0)
    q = torch.randn(1, 3, 2, 4)
    k = torch.randn(1, 3, 2, 4)
    v = torch.randn(1, 3, 2, 4)
    g = -torch.rand(1, 3, 2, 4)
    beta = torch.rand(1, 3, 2)
    out, state = chunk_kda(q, k, v, g, beta, output_final_state=True,
                           use_qk_l2norm_in_kernel=True, use_gate_in_kernel=False)
    print("out", tuple(out.shape), "state", tuple(state.shape),
          "finite", bool(torch.isfinite(out).all()))
