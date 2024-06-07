# main.py

from jsontohtm import HTMLWriter

if __name__ == "__main__":
    writer = HTMLWriter()
    result = writer.htmlwriter("structuredData.json")
    print("whole para:", writer.resume_content)  # Print the global variable containing all paragraph text
