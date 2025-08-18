# roblox-Model2Png
FBX, OBJ 형식의 3D 모델에서 자동으로 PNG 썸네일을 생성합니다.
ViewportFrame으로 아이콘을 만들 때 발생하는 해상도 저하 문제를 해결하기 위해 제작했습니다.

require : blender 4.0 이상


```cmd
& "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe...블렌더 경로" --factory-startup -b -P "C:\Users\...model2png.py..소스 경로" 
  --input "C:\Users\...input 파일 경로(폴더)" `
  --output "C:\Users\...output 파일 경로(폴더)" `
  --res 512 \\ image resolution
  --bg transparent \\ 투명배경 유무
  --angle 30 30 \\ 모델 각도 설정
  --margin 2.0 \\ 카메라와의 거리라고 생각하시면 편합니다
  --ext obj fbx \\ input 확장자 설정
```



Output :

<img width="848" height="488" alt="image" src="https://github.com/user-attachments/assets/20aeea74-4d4d-47d5-aa77-b0fa293b635e" />
