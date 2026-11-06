# Chapter 26

The catalogue edit happened at 04:12 on Friday morning, and Ilsa watched it happen because she had set an alert on the object.

The alert was a watch on the record, not on the orbit: it emailed her whenever any field in K-7741's entry changed. She had set it on Wednesday, using the analyst tools, and she had not told anybody, because telling somebody would have been the same as asking permission.

At 04:12 the epoch changed. The new epoch was 04:09, three minutes old, from an observation the system attributed to dish six. The covariance shrank by a factor of four. The classification stayed debris. The watch item was cleared, with the note *object re-observed, covariance improved, no action*.

She was awake, because she had not slept much, and she was at the kitchen table with the laptop, and she read the alert twice before she understood what it meant.

An epoch update at four in the morning was normal. Dishes observed objects all night. A covariance that improved by a factor of four was not normal: it required a much better observation geometry than a single pass, or it required somebody to type a smaller number into a field.

She opened the observation. Dish six had not been tasked on K-7741 at 04:09. Dish six had been tasked on a geostationary calibration source, which was a fixed point in the sky, and the observation log had no entry for K-7741 at all.

The epoch was a fabrication with a plausible timestamp.

She sat in the dark kitchen with the laptop and the cold tea, and she felt the specific coldness of realising that somebody had done this before, and had done it well enough that the system accepted it, and that the system would accept it again.

She called Femi at 04:30. He answered on the second ring, awake, because he had been awake too.

"The epoch's been rewritten," she said.

"I saw." His voice was flat. "I've been watching the same alert since Wednesday. I didn't want to say."

"Who can write an epoch?"

"Any analyst with catalogue write access. Which is eleven people. Which is all of us."

"Who was in the building at four?"

"The night shift is Voss and two analysts. I checked the badge log at 04:20." A pause. "Voss badged in at 03:55. The other two badged in at 22:00 and haven't left."

"Which one has write access to dish six tasking?"

"Voss does. So does Priya. So do you."

She looked at the laptop. The alert was still on the screen, the new epoch, the shrunken covariance, the cleared watch item.

"Femi. Can you restore the previous version?"

"The system keeps versions for thirty days. I can pull the old one. I can't put it back without a change record, and a change record needs a reason, and the reason field has a drop-down."

"What's in the drop-down?"

"'Correction of clerical error', 'instrument recalibration', 'client instruction'." He said the last one without inflection.

"Use the first one."

"That's a lie."

"It's a description of what happened. Somebody made a clerical error. We're correcting it."

He was quiet for a moment.

"Okay," he said. "I'll do it at 08:00 when the day shift is in, so there are witnesses. And Ilsa—"

"Yes."

"If they've done it once, they'll do it again. The version history is a record, but the record is in the same system as the thing it records."

"I know."

"I just wanted to say it out loud."

She hung up and sat in the kitchen until the sky went grey, and at 06:40 she drove to the station, and at 07:10 she found that her access to the catalogue write function had been suspended pending a review of her "recent classification activity".

The tasking request was in the dish scheduler's log, and the log was a file that the scheduler wrote every night at midnight.

Ilsa pulled the log for Thursday night and read it in the order the scheduler had written it.

At 23:50 the scheduler had queued the standard night list: forty-one objects, eleven dishes, four hours. At 00:04 a priority request had been inserted at the top of the list, ahead of the standard objects, with a note that said *manual insertion, duty officer*.

The request had no object number. The request had coordinates.

Coordinates were unusual. The scheduler worked in object numbers, because the scheduler's job was to point dishes at things the catalogue knew about. A coordinate request was a request to look at a place rather than a thing, and the scheduler had a field for it, and the field was used about twice a year for calibration.

The coordinates were K-7741's predicted position at 04:09.

The dish that had been tasked was dish six.

She sat with that for a while. Whoever had inserted the request had known where the object would be, which meant they had known the object's orbit, which meant they had known the object existed. The insertion had been made at 00:04, which was fourteen minutes after the night shift started and two hours before the access session.

At 02:11 the session had run under her credentials and cleared the watch item. At 04:09 dish six had observed the object, and the covariance had improved by a factor of four, and the classification had stayed debris.

She wrote the three times on a page: 00:04, 02:11, 04:09.

Then she wrote the question: *who inserted the request?*

The log said *duty officer*. The duty officer for Thursday night was Voss, and Voss had been on the desk until 06:00, and Voss had told her on Wednesday that he hoped the night analyst would sign the classification change.

She called him at 06:50, which was his off-going hour.

"I've got a tasking request at 00:04," she said. "Coordinates. Dish six. Inserted by the duty officer."

"That's my login."

"Was it you?"

Voss was quiet for a moment. She could hear a kettle.

"No," he said. "I was on the desk. I logged in at 21:40 and I logged out at 06:05, and the session stayed open the whole night because that's how the desk works. Anybody who sat at that terminal could have typed into it."

"Who sat at it?"

"Me. The night analyst. The calibration engineer came through at eleven for the gain check. A facilities contractor came in at one to fix the chair." He paused. "And anybody with a key and a reason."

"Did you see anybody at the terminal at midnight?"

"I was in the comms room at midnight. I was on a call with the station's ground team about the water ration."

"So the terminal was unattended."

"The terminal was in the duty office and I was in the next room, and the door between them was open, and the screen was on." The kettle clicked off. "Merrick, I've been thinking about this since Wednesday. The tasking request is the thing that made the observation happen. Without the observation, the covariance stays big and the object stays a possible anomaly. With the observation, the covariance shrinks and the object becomes a known debris object with a good orbit."

"Which is the shape of an object that's been legitimised."

"Which is the shape of an object that's been legitimised," Voss said. "And whoever did it knew the object's orbit well enough to point a dish at it four hours ahead."

Ilsa looked at the three times on the page.

"Voss. Did you file the log?"

"I filed the log. I file the log every night. The log says duty officer because the log only has one field."

"Then the log is accurate and useless."

"The log is a record of a login," Voss said. "It's not a record of a person. I've been saying that for six years and nobody's ever listened, because the system is designed for the case where the login and the person are the same thing."

The suspension notice was signed by the duty officer. The reason field said *clerical*.
