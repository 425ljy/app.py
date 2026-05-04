import streamlit as st
import os

# [에러 방지 패치] Pillow 버전 문제를 코드 레벨에서 한 번 더 해결
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.Resampling.LANCZOS
except Exception:
    pass

from moviepy.editor import VideoFileClip, ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips
import tempfile

st.set_page_config(page_title="도장 홍보 숏츠 메이커 v2.1", layout="centered")

st.title("🥋 도장 홍보 숏츠 제작기")
st.warning("⚠️ 고용량 영상(100MB 이상)은 한 번에 1~2개씩만 올리는 것을 권장합니다.")

# 파일 업로드 (다중 선택)
uploaded_files = st.file_uploader("파일 선택 (영상은 짧은 클립이 좋습니다)", 
                                  type=['mp4', 'mov', 'jpg', 'jpeg', 'png'], 
                                  accept_multiple_files=True)

top_text = st.text_input("상단 문구", "오늘의 수련 모습")
bottom_text = st.text_input("하단 문구", "신입 모집중")

if uploaded_files:
    st.write(f"✅ 선택된 파일: {len(uploaded_files)}개")
    
    if st.button("🚀 제작 시작"):
        with st.spinner('편집 중... 잠시만 기다려 주세요.'):
            try:
                clips = []
                temp_files = []

                for uploaded_file in uploaded_files:
                    # 파일 용량 체크 (메모리 부족 방지)
                    if uploaded_file.size > 150 * 1024 * 1024: # 150MB 제한
                        st.error(f"'{uploaded_file.name}' 용량이 너무 커서 제외되었습니다. (150MB 이하 권장)")
                        continue

                    suffix = os.path.splitext(uploaded_file.name)[1].lower()
                    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    tfile.write(uploaded_file.read())
                    temp_files.append(tfile.name)
                    
                    if suffix in ['.jpg', '.jpeg', '.png']:
                        clip = ImageClip(tfile.name).set_duration(1) # 1초
                    else:
                        clip = VideoFileClip(tfile.name)
                    
                    # 9:16 비율 맞추기
                    w, h = clip.size
                    if w/h > 9/16:
                        new_w = h * (9/16)
                        clip = clip.crop(x_center=w/2, width=new_w)
                    clip = clip.resize(height=1280)
                    clips.append(clip)

                if clips:
                    final_clip = concatenate_videoclips(clips, method="compose")
                    
                    # 자막 생성 (폰트 경로 에러 방지를 위해 기본 폰트 사용 시도)
                    txt_top = TextClip(top_text, fontsize=50, color='white', font="NanumGothic-Bold", size=(720, 200), method='caption').set_position(('center', 100)).set_duration(final_clip.duration)
                    txt_bottom = TextClip(bottom_text, fontsize=40, color='yellow', font="NanumGothic-Bold", size=(720, 200), method='caption').set_position(('center', 1050)).set_duration(final_clip.duration)

                    final_video = CompositeVideoClip([final_clip, txt_top, txt_bottom])
                    
                    output_path = "final_shorts.mp4"
                    # 속도를 위해 fps를 조금 낮춤
                    final_video.write_videofile(output_path, fps=20, codec="libx264", audio_codec="aac")
                    
                    st.success("완성되었습니다!")
                    st.video(output_path)
                    with open(output_path, "rb") as file:
                        st.download_button("📥 영상 다운로드", file, file_name="shorts.mp4")
                else:
                    st.error("처리할 수 있는 파일이 없습니다.")

            except Exception as e:
                st.error(f"오류 발생: {e}")
            finally:
                for f in temp_files:
                    if os.path.exists(f): os.remove(f)
