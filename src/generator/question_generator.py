from langchain.output_parsers import PydanticOutputParser
from src.models.question_schemas import MCQuestion,FillBlankQuestion
from src.prompts.templates import mcq_prompt_template,fill_blank_prompt_template
from src.llm.groq_client import get_groq_llm
from src.config.settings import settings
from src.common.logger import get_logger
from src.common.custom_exception import CustomException

class QuestionGenerator:
    def __init__(self):
        self.llm = get_groq_llm()
        self.logger = get_logger(self.__class__.__name__)

    def _retry_and_parse(self,prompt,parser,topic,difficulty):
        
        for attempt in range(settings.MAX_RETRIES):
            try:
                self.logger.info(f"Generating question for topic {topic} with difficulty {difficulty}")

                response = self.llm.invoke(prompt.format(topic=topic,difficulty=difficulty))
                print(response.content)
                parsed = parser.parse(response.content)
                print(parsed)
                self.logger.info("Successfully Parsed the question")

                return parsed

            except Exception as e:
                self.logger.error(f"Error comming : {str(e)}")

                if attempt == settings.MAX_RETRIES - 1:
                    raise CustomException(f"Generation failed after {settings.MAX_RETRIES}",e)
                
    
    def generate_mcq(self,topic:str, difficulty:str="medium") -> MCQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=MCQuestion)

            question = self._retry_and_parse(mcq_prompt_template,parser,topic,difficulty)

            if len(question.options) != 4 or question.correct_answer not in question.options:
                raise ValueError("Invalid MCQ Structure")
            self.logger.info("Generated Valid MCQ Question")
            return question
        
        except Exception as e:
            self.logger.error(f"Failed to generate MCQ : {str(e)}")
            raise CustomException("MCQ Generation Failed",e)
        

    def generate_fill_blank(self,topic:str, difficulty:str="medium") -> FillBlankQuestion:
        try:
            parser = PydanticOutputParser(pydantic_object=FillBlankQuestion)

            question = self._retry_and_parse(fill_blank_prompt_template,parser,topic,difficulty)

            if "___" not in question.question:
                raise ValueError("Fill in the blanks should contain '___'")
            

            self.logger.info("Generated Valid Fill in the Blanks Question")
            return question
        
        except Exception as e:
            self.logger.error(f"Failed to generate Fillups : {str(e)}")
            raise CustomException("Fill in blanks Generation Failed",e)


