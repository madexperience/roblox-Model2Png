# roblox-Model2Png
fbx,obj 확장자 모델 파일들의 이미지 썸네일(png)을 자동으로 뽑아줍니다.

require : blender 4.0 이상


```cmd
& "C:\Program Files\Blender Foundation\Blender 4.4\blender.exe...블렌더 경로" --factory-startup -b -P "C:\Users\...model2png.py..소스 경로" -- `
  --input "C:\Users\...input 파일 경로(폴더)" `
  --output "C:\Users\...output 파일 경로(폴더)" `
  --res 512 \\ 이미지 resize
  --bg transparent \\ 투명배경 유무
  --angle 30 30 \\ 모델 각도 설정
  --margin 2.0 \\ 마진 설정
  --ext obj fbx \\ input 확장자 설정
```



Output :
<img width="848" height="488" alt="image" src="https://github.com/user-attachments/assets/20aeea74-4d4d-47d5-aa77-b0fa293b635e" />
