# human-like-mouse-mover
Package contains a class which is trying to perform some human-like mouse movements <br>
<br>
---
## Realization details
Method uses outer functions for moving mouse and clicking. Base method of curve generation - Bezier curves. <br>
Implemented functionality:
- [x] Random linear interpolation: some parts of the curve may be interpolated as straight lines so the movements become more antsy
- [x] Random angular edges on the curve
- [x] Distortion
- [x] Movement direction may change slightly, also randomly
- [x] Acceleration may slow down as well as speed up during the movement
- [x] Acceleration almost always slows down on the curve's end
- [x] Fake cliks: simulation of the human exessive clicking (optional)
- [ ] Tremor
---
## Some examples: <br>
![image](https://github.com/Averlex/human-like-curves/assets/115068777/e4546e82-f80e-4618-930f-55f1cdf1a8a3) <br>
![image](https://github.com/Averlex/human-like-curves/assets/115068777/78f467ad-633f-4397-a68f-fb1800104e8f) <br>
![image](https://github.com/Averlex/human-like-curves/assets/115068777/e5d194c4-4e73-48fb-bf32-c02d782ee818) <br>
![image](https://github.com/Averlex/human-like-curves/assets/115068777/b7acebb9-35ba-4ced-9428-802c7eb2fd75) <br>
![image](https://github.com/Averlex/human-like-curves/assets/115068777/b2889d08-7e51-4b28-bd2a-6d7a7ea0b6a0) <br>
![image](https://github.com/Averlex/human-like-curves/assets/115068777/5085f2b6-02ca-4787-a83a-364c335f6e69) <br>

---
### CREDENTIALS <br>
Thanks patrikoss for some basic functionality: <br>
https://github.com/patrikoss/pyclick <br>
