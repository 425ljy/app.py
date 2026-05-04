import streamlit as st
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import tempfile
import os

st.set_page_config(page_title="도장 홍보 숏츠 메이커", layout="centered")

st.title("🥋 도장 홍보 숏츠 자동 제작 (다중 선택)")
st.write("여러 영상을 선택하면 순서대로 합쳐서 숏츠를 만듭니다.")

# 1. 파일 업로드 (accept_multiple_files=True 추가)
uploaded_files = st.file_uploader("원본 영상들 선택 (여러 개 가능)", type=['mp4', 'mov'], accept_multiple_files=True)

top_text = st.text_input("상단 문구", "강력한 발차기!")
bottom_text = st.text_input("하단 문구", "OO도장 신입 모집 중")
text_color = st.color_picker("글자 색상", "#FFFFFF")

if uploaded_files:
    st.write(f"현재 {len(uploaded_files)}개의 영상이 선택되었습니다.")
    
    if st.button("🚀 합쳐서 영상 제작 시작"):
        with st.spinner('여러 영상을 합치고 편집 중입니다... 시간이 좀 걸릴 수 있어요!'):
            clips = []
            temp_files = []

            for uploaded_file in uploaded_files:
                # 개별 파일 임시 저장
                tfile = tempfile.NamedTemporaryFile(delete=False)
                tfile.write(uploaded_file.read())
                temp_files.append(tfile.name)
                
                # 영상 처리 및 비율 조정
                clip = VideoFileClip(tfile.name)
                w, h = clip.size
                target_ratio = 9/16
                if w/h > target_ratio:
                    new_w = h * target_ratio
                    clip = clip.crop(x_center=w/2, width=new_w)
                clip = clip.resize(height=1280)
                clips.append(clip)

            # 2. 영상 이어 붙이기
            final_clip = concatenate_videoclips(clips, method="compose")

            # 3. 자막 추가
            txt_top = TextClip(top_text, fontsize=50, color=text_color, font="NanumGothic-Bold").set_position(('center', 100)).set_duration(final_clip.duration)
            txt_bottom = TextClip(bottom_text, fontsize=40, color='yellow', font="NanumGothic-Bold").set_position(('center', 1100)).set_duration(final_clip.duration)

            final_video = CompositeVideoClip([final_clip, txt_top, txt_bottom])
            
            # 결과 저장
            output_path = "result_combined.mp4"
            final_video.write_videofile(output_path, fps=24, codec="libx264")
            
            # 4. 결과 출력
            st.video(output_path)
            with open(output_path, "rb") as file:
                st.download_button(label="📥 완성된 영상 다운로드", data=file, file_name="combined_shorts.mp4", mime="video/mp4")
            
            # 임시 파일 삭제
            for f in temp_files:
                if os.path.exists(f): os.remove(f)
