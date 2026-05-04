import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
import tempfile
import os

# 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="도장 홍보 숏츠 메이커", layout="centered")

st.title("🥋 도장 홍보 숏츠 자동 제작")
st.write("영상을 올리고 문구를 입력하면 숏츠가 완성됩니다.")

# 1. 파일 업로드
uploaded_file = st.file_uploader("원본 영상 선택 (MP4)", type=['mp4', 'mov'])

# 2. 문구 입력
top_text = st.text_input("상단 문구", "강력한 발차기!")
bottom_text = st.text_input("하단 문구", "OO도장 신입 모집 중")
text_color = st.color_picker("글자 색상", "#FFFFFF")

if uploaded_file is not None:
    if st.button("🚀 영상 제작 시작"):
        with st.spinner('편집 중입니다... 잠시만 기다려주세요.'):
            # 임시 파일 저장
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())
            
            # MoviePy 편집 로직
            clip = VideoFileClip(tfile.name)
            
            # 9:16 비율 조정 (중앙 크롭)
            w, h = clip.size
            target_ratio = 9/16
            if w/h > target_ratio:
                new_w = h * target_ratio
                clip = clip.crop(x_center=w/2, width=new_w)
            clip = clip.resize(height=1280) # 모바일용 적정 해상도

            # 자막 추가 (간단한 구현을 위해 텍스트 클립 생성)
            # *주의: 서버 환경에 한글 폰트가 설치되어 있어야 함
            txt_top = TextClip(top_text, fontsize=50, color=text_color, font="NanumGothic-Bold")
            txt_top = txt_top.set_position(('center', 100)).set_duration(clip.duration)
            
            txt_bottom = TextClip(bottom_text, fontsize=40, color='yellow', font="NanumGothic-Bold")
            txt_bottom = txt_bottom.set_position(('center', 1100)).set_duration(clip.duration)

            final_video = CompositeVideoClip([clip, txt_top, txt_bottom])
            
            # 결과 저장
            output_path = "result_shorts.mp4"
            final_video.write_videofile(output_path, fps=24, codec="libx264")
            
            # 3. 결과 미리보기 및 다운로드
            st.video(output_path)
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 편집된 영상 다운로드",
                    data=file,
                    file_name="dojang_shorts.mp4",
                    mime="video/mp4"
                )
