from app.ui.widgets.log_view import LogView
from app.ui.widgets.model_card import ModelCard
from app.ui.widgets.status_card import StatusCard


def test_status_card_updates_title_value_and_detail(qtbot):
    card = StatusCard("显卡", "检测中", "等待检测")
    qtbot.addWidget(card)

    card.set_status("RTX 4070", "CUDA 12.4")

    assert card.title_label.text() == "显卡"
    assert card.value_label.text() == "RTX 4070"
    assert "CUDA 12.4" in card.detail_label.text()


def test_model_card_emits_selection_change(qtbot):
    card = ModelCard("yolov8", "YOLOv8", ["n", "s"], suffix="")
    qtbot.addWidget(card)
    changes = []
    card.selection_changed.connect(lambda: changes.append(card.selected_weight()))

    card.checkbox.setChecked(True)
    card.scale_combo.setCurrentText("s")

    assert changes
    assert card.selected_weight() == "yolov8s.pt"
    assert card.size_label.text() == "可选权重"


def test_log_view_truncates_long_lines(qtbot):
    log = LogView(max_lines=4, max_line_length=5)
    qtbot.addWidget(log)

    for line in ["abcdef", "two", "three", "four"]:
        log.append_line(line)

    text = log.toPlainText()
    assert "abcde" in text
    assert len(text.splitlines()) == 4


def test_log_view_keeps_line_limit(qtbot):
    log = LogView(max_lines=3, max_line_length=20)
    qtbot.addWidget(log)

    for line in ["one", "two", "three", "four"]:
        log.append_line(line)

    text = log.toPlainText()
    assert "one" not in text
    assert text.splitlines() == ["two", "three", "four"]
