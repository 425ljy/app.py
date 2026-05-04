import streamlit as st
from moviepy.editor import VideoFileClip, ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips
import tempfile
import os

# 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="도장 홍보 숏츠 메이커 v2.0", layout="centered")

# CSS를 이용해 제목 디자인 개선
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E88E5; text-align: center; }
    .sub-title { font-size: 18px; color: #555; text-align: center; margin-bottom: 20px; }
    </style>
    <div class="main-title">🥋 도장 홍보 숏츠 메이커 v2.0</div>
    <div class="sub-title">사진 1초 전환 적용 완료! 더 빠른 속도감의 홍보 영상</div>
    """, unsafe_allow_html=True)

# 1. 파일 업로드 (다중 선택 지원)
uploaded_files = st.file_uploader("사진(JPG/PNG)이나 영상(MP4/MOV)을 선택하세요.", 
                                  type=['mp4', 'mov', 'jpg', 'jpeg', 'png'], 
                                  accept_multiple_files=True)

# 2. 문구 및 설정
col1, col2 = st.columns(2)
with col1:
    top_text = st.text_input("상단 홍보 문구", "오늘의 수련 하이라이트")
with col2:
    bottom_text = st.text_input("하단 홍보 문구", "신입 모집중 | 010-XXXX-XXXX")

text_color = st.color_picker("글자 색상 선택", "#FFFFFF")

if uploaded_files:
    st.info(f"총 {len(uploaded_files)}개의 파일이 선택되었습니다.")
    
    if st.button("🚀 1초 전환 숏츠 제작 시작"):
        with st.spinner('영상을 제작 중입니다. 잠시만 기다려 주세요...'):
            try:
                clips = []
                temp_files = []

                for uploaded_file in uploaded_files:
                    # 임시 파일 저장 (확장자 유지)
                    suffix = os.path.splitext(uploaded_file.name)[1].lower()
                    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                    tfile.write(uploaded_file.read())
                    temp_files.append(tfile.name)
                    
                    # 파일 형식에 따른 클립 생성
                    if suffix in ['.jpg', '.jpeg', '.png']:
                        # 사진인 경우: ★요청하신 대로 1초만 보여줌★
                        clip = ImageClip(tfile.name).set_duration(1)
                    else:
                        # 영상인 경우
                        clip = VideoFileClip(tfile.name)
                    
                    # 9:16 비율 맞추기 (숏츠 규격)
                    w, h = clip.size
                    if w/h > 9/16:
                        # 가로가 넓은 경우 중앙 크롭
                        new_w = h * (9/16)
                        clip = clip.crop(x_center=w/2, width=new_w)
                    
                    # 해상도 통일 (HD급 숏츠)
                    clip = clip.resize(height=1280)
                    clips.append(clip)

                # 모든 클립 하나로 합치기
                final_clip = concatenate_videoclips(clips, method="compose")

                # 자막 추가 (가운데 정렬)
                txt_top = TextClip(top_text, fontsize=50, color=text_color, font="NanumGothic-Bold", method='caption', size=(720, 200))
                txt_top = txt_top.set_position(('center', 80)).set_duration(final_clip.duration)
                
                txt_bottom = TextClip(bottom_text, fontsize=40, color='yellow', font="NanumGothic-Bold", method='caption', size=(720, 200))
                txt_bottom = txt_bottom.set_position(('center', 1050)).set_duration(final_clip.duration)

                final_video = CompositeVideoClip([final_clip, txt_top, txt_bottom])
                
                # 결과물 저장
                output_path = "final_dojang_shorts.mp4"
                final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
                
                # 제작 완료 알림 및 다운로드 버튼
                st.success("✅ 제작 완료!")
                st.video(output_path)
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 완성된 숏츠 다운로드",
                        data=file,
                        file_name="dojang_promotion_shorts.mp4",
                        mime="video/mp4"
                    )

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
            finally:
                # 사용한 임시 파일 정리
                for f in temp_files:
                    if os.path.exists(f):
                        try: os.remove(f)
                        except: pass
