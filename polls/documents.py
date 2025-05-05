from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch.dsl import analyzer, tokenizer
from .models import Question

autocomplete_analyzer = analyzer('autocomplete_analyzer',
            tokenizer=tokenizer('trigram', 'ngram', min_gram=3, max_gram=20),
            filter=['lowercase']
        )

@registry.register_document
class QuestionDocument(Document):
    class Index:
        name = 'questions'
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "max_ngram_diff": 20
        }

    question_text = fields.TextField(
        analyzer=autocomplete_analyzer,
    )

    class Django:
        model = Question
        fields = [
            'id',
            'deadline',
        ]