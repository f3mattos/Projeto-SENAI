"""Testes de unidade para o classificador de urgência."""
import pytest
from classifier.service import UrgencyClassifier


def test_classifier_loads_successfully():
    classifier = UrgencyClassifier()
    assert classifier is not None


def test_empty_input_raises_value_error():
    classifier = UrgencyClassifier()
    with pytest.raises(ValueError):
        classifier.predict("   ")


def test_high_urgency_prediction():
    classifier = UrgencyClassifier()
    res = classifier.predict("O sistema principal está fora do ar e bloqueando faturamento!")
    assert res["urgencia"] == "alta"
    assert res["confianca"] >= 0.5


def test_low_urgency_prediction():
    classifier = UrgencyClassifier()
    res = classifier.predict("Como alterar a foto do perfil no sistema?")
    assert res["urgencia"] == "baixa"
    assert res["confianca"] >= 0.5
