from .documents import QuestionDocument


def search_questions(query):
    search_results = QuestionDocument.search().query("multi_match", query=query,
                                                     fields=[
                                                         'question_text',
                                                     ], )

    return search_results
