import os
import streamlit as st
from dotenv import load_dotenv
from src.utils.helpers import *
from src.generator.question_generator import QuestionGenerator
load_dotenv()

def main():
    st.set_page_config(page_title="Studdy Buddy AI", page_icon="👩‍🦳")

    if "quiz_manager" not in st.session_state:
        st.session_state.quiz_manager = QuizManager()

    if "quiz_generated" not in st.session_state:
        st.session_state.quiz_generated = False

    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False

    if "rerun_trigger" not in st.session_state:
        st.session_state.rerun_trigger = False

    st.title("Study Buddy AI")

    st.sidebar.header("Quiz Setting")

    question_type = st.sidebar.selectbox(
        "Select Question Type",
        ["Multiple Choice","Fill in the blank"],
        index=0
    )

    topic = st.sidebar.text_input("Enter the topic",placeholder="Indian History, Geography")

    difficulty = st.sidebar.selectbox(
        "Difficulty Level",
        ["Easy","Medium","Hard"],
        index=1
    )

    num_questions = st.sidebar.number_input(
        "Number of Questions",
        min_value=1, max_value=10, value=5
        
    )

    if st.sidebar.button("Generate Quiz"):
        st.session_state.quiz_submitted = False

        generator = QuestionGenerator()
        success = st.session_state.quiz_manager.generate_questions(
            generator,
            topic,
            question_type,
            difficulty,
            num_questions
        )

        st.session_state.quiz_generated = success
        rerun()

    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.header("Quiz")
        st.session_state.quiz_manager.attempt_quiz()

        if st.button("Submit Quiz"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            rerun()

    if st.session_state.quiz_submitted:
        st.header("Quiz Result")
        result_df = st.session_state.quiz_manager.generate_result_dataframe()

        if not result_df.empty:
            correct_count = result_df["is_correct"].sum()
            total_questions = len(result_df)
            score_percentage = (correct_count/total_questions)*100
            st.write(f"Score :{score_percentage} ")

            for _, result in result_df.iterrows():
                question_num = result["question_num"]
                if result["is_correct"]:
                    st.success(f"Question {question_num} : {result["question"]} Correct Answer")

                else:
                    st.error(f"Question {question_num} : {result["question"]} Wrong Answer")
                    st.write(f"Your Answer : {result["user_ans"]}")
                    st.write(f"Correct answer : {result["correct_answer"]}")

                st.markdown("--------")

            if st.button("Save results"):
                saved_file = st.session_state.quiz_manager.save_to_csv()
                if saved_file:
                    with open(saved_file,"rb") as f:
                        st.download_button(
                            label="Download",
                            data=f.read(),
                            file_name=os.path.basename(saved_file),
                            mime = "text/csv"
                        )

                else:
                    st.warning("No results Available")

if __name__ == "__main__":
    main()
