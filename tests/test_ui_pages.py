from app.core.detector import CondaInfo, EnvSnapshot, GpuInfo
from app.ui.pages.detect_page import DetectPage
from app.ui.pages.install_page import InstallPage
from app.ui.pages.select_page import SelectPage


def snapshot():
    return EnvSnapshot(
        os="Windows 10",
        is_windows_supported=True,
        conda=CondaInfo("conda.exe", "conda 24", ["base"]),
        gpu=GpuInfo("RTX 4070", "550.78", 12282, "12.4"),
        free_disk_gb=88.5,
        mirror_reachable=True,
    )


def test_detect_page_renders_snapshot(qtbot):
    page = DetectPage()
    qtbot.addWidget(page)

    page.set_snapshot(snapshot())

    assert page.os_card.value_label.text() == "Windows 10"
    assert page.gpu_card.value_label.text() == "RTX 4070"
    assert page.next_button.isEnabled()


def test_select_page_defaults_and_builds_config(qtbot, tmp_path):
    page = SelectPage()
    qtbot.addWidget(page)
    page.workspace_edit.setText(str(tmp_path))

    page.select_weight("yolov8n.pt")
    config = page.build_config()

    assert "yolov8n.pt" in config["weights"]
    assert config["env_name"] == "yolo-env"
    assert config["workspace"] == str(tmp_path)


def test_select_page_warns_for_non_ascii_workspace(qtbot):
    page = SelectPage()
    qtbot.addWidget(page)

    page.workspace_edit.setText(r"C:\Users\用户\workspace")
    page.validate_paths()

    assert "non-ASCII" in page.path_warning_label.text()
    assert not page.start_button.isEnabled()


def test_install_page_tracks_steps_and_log(qtbot):
    page = InstallPage()
    qtbot.addWidget(page)

    page.set_step("detect", "running")
    page.append_log("hello")
    page.set_finished(True, "")

    assert page.step_labels["detect"].text().endswith("running")
    assert "hello" in page.log_view.toPlainText()
    assert page.try_button.isEnabled()


def test_install_page_exposes_uninstall_button(qtbot):
    page = InstallPage()
    qtbot.addWidget(page)

    assert page.uninstall_button.text() == "Uninstall environment"
    assert not page.uninstall_button.isEnabled()
