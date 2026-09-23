"""Amostra manual já usada no Android; nunca consulta Instagram ou IA."""

DEMO_URL = "https://www.instagram.com/p/DdC8Aw1RQU4/"
DEMO_CODE = "DdC8Aw1RQU4"


def recipe():
    ingredients = [
        ("Fraldinha", None), ("Sal", None), ("Páprica defumada", None),
        ("Pimenta-do-reino", None), ("Batatas", "4 ou 5"), ("Azeite", None),
        ("Orégano", None), ("Cebola", None), ("Alho", "5 dentes"),
        ("Manteiga para dourar o alho", None), ("Farinha panko", None),
        ("Queijo muçarela", None), ("Salsinha e cebolinha", None),
        ("Manteiga em ponto de pomada", "1/2 colher"),
    ]
    steps = [
        "Tempere a fraldinha com sal, páprica defumada e pimenta-do-reino. Tempere as batatas separadamente com azeite, sal, páprica defumada e orégano.",
        "Forre a forma com cebola, coloque a carne e as batatas e cubra com papel-alumínio. Asse a 220 °C por 45 minutos.",
        "Retire o papel-alumínio e deixe no forno por mais 10 a 15 minutos.",
        "Doure os 5 dentes de alho na manteiga. Misture com farinha panko, muçarela, salsinha, cebolinha e 1/2 colher de manteiga em ponto de pomada.",
        "Coloque a mistura sobre a carne e leve para dourar por mais 10 minutos.",
    ]
    return {
        "title": "Fraldinha com crosta de alho e batatas",
        "ingredients": [{"id": i, "name": name, "quantity_text": quantity, "evidence": []}
                        for i, (name, quantity) in enumerate(ingredients)],
        "steps": [{"id": i, "instruction": instruction, "evidence": []}
                  for i, instruction in enumerate(steps)],
        "warnings": ["Amostra transcrita manualmente da legenda, sem extração por IA.",
                     "Há quantidades não informadas. Autoria não registrada na amostra."],
        "language": "pt-BR", "author": None,
    }
