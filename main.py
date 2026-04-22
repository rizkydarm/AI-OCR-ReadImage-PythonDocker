from paddleocr import PaddleOCRVL
import openai

def main():
    print("Hello from ai-read-image!")
    pipeline = PaddleOCRVL(pipeline_version="v1.5")
    output = pipeline.predict("test_image/test1.jpg")
    for res in output:
        res.print()
        res.save_to_json(save_path="output")
        res.save_to_markdown(save_path="output")


if __name__ == "__main__":
    main()
