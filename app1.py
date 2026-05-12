import streamlit as st
import pickle
import nltk
import pandas as pd
import pytesseract as tess
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from googletrans import Translator
from PIL import Image

# Initialize PorterStemmer
ps = PorterStemmer()

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Configure pytesseract path
tess.pytesseract.tesseract_cmd = r'C:\Users\SURJO\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

def transform_text(text):
    text = text.lower()
    text = nltk.word_tokenize(text)
    text = [i for i in text if i.isalnum()]
    stop_words = set(stopwords.words('english'))
    text = [ps.stem(i) for i in text if i not in stop_words]
    return " ".join(text)

@st.cache_data
def preprocess_data(data):
    data['v2'] = data['v2'].apply(transform_text)
    return data

@st.cache_data
def get_model_and_vectorizer():
    with open('model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('vectorizer.pkl', 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)
    return model, vectorizer
def translate_text(input_text):
    # Translate the text to English using Google Translate
    trans = Translator()
    translated_text = trans.translate(input_text, dest="english").text

    return translated_text

def predict_spam(input_text):
    '''
    # Translate the text to English using Google Translate
    trans = Translator()
    translated_text = trans.translate(input_text, dest="english").text
'''
    translated_text = translate_text(input_text)

    st.text_area("Translated Text", value=translated_text, height=200)

    # Load the model and vectorizer
    model, vectorizer = get_model_and_vectorizer()

    # Transform the text using the text preprocessing function
    transformed_text = transform_text(translated_text)

    # Vectorize the transformed text
    vector_input = vectorizer.transform([transformed_text])

    # model, vector_input = translate_text(input_text)

    # Make the prediction
    result = model.predict(vector_input)[0]

    return result

def main():
    # Get the list of all available languages in pytesseract
    available_languages = tess.get_languages(config='')

    # Join the languages list into a string for Tesseract
    languages = '+'.join(available_languages)

    st.title("Email Spam Detector")

    # Option to input message manually or via image
    option = st.selectbox("Choose input type:", ["Text Input", "Upload Image"])

    if option == "Text Input":
        inp = st.text_area("Enter the message")

        if st.button('Predict'):
            result = predict_spam(inp)
            if result == 'spam':
                st.header("Spam")
            else:
                st.header("Not Spam")

    elif option == "Upload Image":
        # Image upload functionality
        uploaded_image = st.file_uploader("Upload an image", type=['jpg', 'png', 'jpeg'])

        if uploaded_image is not None:
            # Open the image and use pytesseract to extract text
            img = Image.open(uploaded_image)
            extracted_text = tess.image_to_string(img, lang=languages)

            # Replace newline characters with a space and strip any extra spaces
            complete_sentence = extracted_text.replace('\n', ' ').strip()

            # Replace multiple spaces with a single space
            complete_sentence = ' '.join(complete_sentence.split())
            
            trans_text = translate_text(complete_sentence)
            st.text_area("Extracted Text", value=complete_sentence, height=200)

            # Predict spam based on extracted text
            if st.button('Predict from Image Text'):
                result = predict_spam(trans_text)
                if result == 'spam':
                    st.header("Spam")
                else:
                    st.header("Not Spam")

if __name__ == "__main__":
    data = pd.read_csv(r'E:\project\Sem 6\FDS DA\spam.csv', encoding='latin-1')
    data = preprocess_data(data)
    main()
