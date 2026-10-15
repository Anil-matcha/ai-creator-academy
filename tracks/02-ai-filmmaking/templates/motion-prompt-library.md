# Motion Prompt Library

Use these pre-tested camera direction phrases in your text-to-video and image-to-video prompts to control motion dynamics.

---

## 1. Dolly & Tracking Shots
Move the camera physically closer, further, or alongside the character.
* **Dolly In / Push-in:**
  > `"Slow cinematic dolly in, camera slowly pushes toward the character's face, high quality, 24fps."`
* **Dolly Out / Pull-back:**
  > `"Cinematic dolly out, camera pulls back to reveal the surrounding environment, wide shot."`
* **Tracking / Lateral Follow:**
  > `"Tracking shot, camera moves parallel to the character as they walk down the hallway, side profile view."`

## 2. Pan, Tilt, and Roll
Rotate the camera from a fixed point.
* **Pan Left/Right:**
  > `"Camera slowly pans left, revealing the landscape, cinematic movement."`
* **Tilt Up/Down:**
  > `"Slow camera tilt up, starting from the boots on the wet ground up to the character's face."`
* **Dutch Angle / Roll:**
  > `"Dutch angle, subtle camera roll to create tension, moody cinema style."`

## 3. Advanced Cinematography Actions
* **Dolly Zoom (Vertigo Effect):**
  > `"Subtle dolly zoom effect, background compresses while character remains size-consistent, high tension."`
* **Whip Pan:**
  > `"Fast whip pan transition to the right, motion blur, clean cut."`
* **Drone Crane Shot:**
  > `"High angle crane shot, camera slowly rises vertically, looking down on the streets below."`

## 4. Movement Control Tips
* **Start and End Frames:** If your tool supports image-to-video with a start and end frame, place the static composition at start frame and the final target framing at end frame. The AI will interpolate the movement.
* **Motion Strength Slider:**
  * **Low (1-3):** Best for portrait dialogues, subtle wind in hair, slow lighting shifts.
  * **Medium (4-7):** Best for walking, slow camera pan/tilt, pouring water.
  * **High (8-10):** Best for action sequences, driving cars, running shots (be prepared for higher morphing/artifacts).
