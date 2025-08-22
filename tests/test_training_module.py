from src.foodops_pro.training import TrainingPath, TrainingModule, QuizQuestion


def test_training_path_progress_and_certificate(tmp_path):
    modules = [
        TrainingModule(
            name="Module 1",
            objective="Objectif 1",
            quiz=[QuizQuestion("Q1", ["A", "B"], 0)],
        ),
        TrainingModule(
            name="Module 2",
            objective="Objectif 2",
            quiz=[QuizQuestion("Q2", ["A", "B"], 1)],
        ),
    ]
    path = TrainingPath(modules)

    # Répondre correctement au premier quiz
    assert path.answer_current_quiz(0)
    assert path.current_index == 1

    # Mauvaise réponse au second quiz
    assert not path.answer_current_quiz(0)
    assert path.current_index == 1

    # Bonne réponse et génération de certificat
    assert path.answer_current_quiz(1)
    assert path.is_completed()
    cert_file = tmp_path / "cert.txt"
    cert_text = path.generate_certificate("Alice", filename=cert_file)
    assert "Alice" in cert_text
    assert cert_file.read_text(encoding="utf-8") == cert_text
