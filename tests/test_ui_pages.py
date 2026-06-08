from app.core.detector import CondaInfo, EnvSnapshot, GpuInfo
from app.ui.pages.detect_page import DetectPage
from app.ui.pages.install_page import InstallPage
from app.ui.pages import select_page
from app.ui.pages.select_page import SelectPage


def snapshot():
    return EnvSnapshot(
        os="Windows 10",
        is_windows_supported=True,
        conda=CondaInfo("conda.exe", "conda 24", ["base", "ultralytics", "yolo"]),
        gpu=GpuInfo("RTX 4070", "550.78", 12282, "12.4"),
        disk_root="D:",
        free_disk_gb=88.5,
        mirror_reachable=True,
    )


def test_detect_page_renders_snapshot(qtbot):
    page = DetectPage()
    qtbot.addWidget(page)

    page.set_snapshot(snapshot())

    assert page.os_card.value_label.text() == "Windows 10"
    assert page.gpu_card.value_label.text() == "RTX 4070"
    assert page.disk_card.value_label.text() == "D: 88.5 GB 可用"
    assert page.conda_envs_label.text() == "base, ultralytics, yolo"
    assert page.next_button.isEnabled()


def test_select_page_defaults_and_builds_config(qtbot, tmp_path):
    page = SelectPage()
    qtbot.addWidget(page)
    page.workspace_edit.setText(str(tmp_path))
    assert page.python_version_combo.currentText() == "3.10"
    assert page.python_version_combo.isEditable()
    assert [page.python_version_combo.itemText(i) for i in range(page.python_version_combo.count())] == [
        "3.10",
        "3.11",
        "3.12",
    ]
    assert page.build_config()["weights"] == []
    assert page.start_button.isEnabled()
    assert page.model_cards == []
    assert page.title_label.text() == "YOLO 环境安装配置"
    assert "安装目录" in page.install_dir_label.text()
    assert "安装目录" in page.summary_label.text()

    page.python_version_combo.setEditText("3.12")
    config = page.build_config()

    assert config["weights"] == []
    assert config["env_name"] == "yolo-env"
    assert config["python_version"] == "3.12"
    assert config["workspace"] == str(tmp_path)


def test_select_page_uses_split_install_layout(qtbot):
    page = SelectPage()
    qtbot.addWidget(page)

    assert page.side_panel.objectName() == "selectSidePanel"
    assert page.side_title_label.text() == "YOLO 环境工具"
    assert "专注安装可用环境" in page.side_description_label.text()
    assert "检测 Conda 与显卡" in page.side_steps_label.text()
    assert "创建独立 YOLO 环境" in page.side_steps_label.text()
    assert page.install_config_panel.objectName() == "installConfigPanel"
    assert page.panel_title_label.text() == "安装目录与环境参数"
    assert page.total_label.text() == "模型权重：不下载"


def test_select_page_warns_for_non_ascii_workspace(qtbot):
    page = SelectPage()
    qtbot.addWidget(page)

    page.workspace_edit.setText(r"C:\Users\用户\workspace")
    page.validate_paths()

    assert "中文" in page.path_warning_label.text()
    assert not page.start_button.isEnabled()


def test_select_page_suggests_non_c_drive_without_blocking(qtbot):
    page = SelectPage()
    qtbot.addWidget(page)

    page.workspace_edit.setText(r"C:\YoloInstaller\workspace")
    page.validate_paths()

    assert "C 盘" in page.path_warning_label.text()
    assert page.start_button.isEnabled()


def test_select_page_can_choose_workspace_directory(qtbot, monkeypatch, tmp_path):
    chosen_dir = tmp_path / "manual_workspace"

    monkeypatch.setattr(
        select_page.QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(chosen_dir),
    )

    page = SelectPage()
    qtbot.addWidget(page)

    page.browse_workspace_button.click()

    assert page.workspace_edit.text() == str(chosen_dir)
    assert page.build_config()["workspace"] == str(chosen_dir)


def test_install_page_tracks_steps_and_log(qtbot):
    page = InstallPage()
    qtbot.addWidget(page)

    page.set_step("detect", "running")
    page.append_log("hello")
    page.set_finished(True, "")

    assert page.step_labels["detect"].text().endswith("运行中")
    assert "hello" in page.log_view.toPlainText()
    assert page.try_button.isEnabled()


def test_install_page_exposes_uninstall_button(qtbot):
    page = InstallPage()
    qtbot.addWidget(page)

    assert page.uninstall_env_edit.text() == "yolo-env"
    assert page.uninstall_button.text() == "卸载环境"
    assert not page.uninstall_button.isEnabled()
