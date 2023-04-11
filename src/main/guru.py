import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QApplication, QProgressBar, QFileDialog, QLabel, QHBoxLayout

from src.main.open_log_status import OpenLogStatus
from src.log.log import Log
from src.configuration.config_manager import ConfigManager
from src.ui.actions import Actions
from src.ui.menubar import MenuBarManager
from src.ui.please_wait import PleaseWait
from src.ui.toolbar import ToolBarManager
from src.graphics.track_analysis_canvas import TrackAnalysisCanvas
from src.tracks.tracks import get_all_tracks
from src.ui.open_file_dialog import OpenFileDialog
from src.ui.icons import get_custom_icon
from src.graphics.track_painter import TrackPainter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #
        # First of all, get config manager up and running so that we have access to any settings that it manages for us
        #
        self._config_manager = ConfigManager()

        # PROTOTYPE FROM HERE

        self.setMinimumSize(200, 200)
        self.resize(1000, 800)
        self.setWindowTitle("DeepRacer Guru")
        self.setWindowIcon(get_custom_icon("window_icon"))

        # Status Bar
        self._please_wait = PleaseWait(self.statusBar())

        # Define UI actions
        self._actions = Actions(self.style())

        # Menu & Tool bars
        self._menu_bar_manager = MenuBarManager(self.menuBar(), self._actions)
        self._tool_bar_manager = ToolBarManager(self.addToolBar("Main"), self._actions)

        # Connect actions with callback methods to implement them
        self._actions.open_file.triggered.connect(self._action_open_file)
        self._actions.file_info.triggered.connect(self._action_file_info)
        self._actions.change_log_directory.triggered.connect(self._action_change_log_directory)
        self._actions.set_file_options.triggered.connect(self._action_set_file_options)
        self._actions.exit.triggered.connect(self._action_exit)

        # Internal variable(s) to communicate from dialogs to main after they are closed
        self._open_file_dialog_chosen_files = None

        # Keep details of current open log and filters etc. in a form easily shared with analyzers etc.
        self._open_log_status = OpenLogStatus()

        # Canvas etc. comments TODO

        self.canvas = TrackAnalysisCanvas()

        centre_layout = QHBoxLayout()
        centre_layout.addWidget(self.canvas)

        analysis_controls_area = QLabel()
        analysis_controls_area.setMinimumWidth(100)
        analysis_controls_area.setMaximumWidth(100)
        centre_layout.addWidget(analysis_controls_area)

        centre_widget = QLabel()
        centre_widget.setLayout(centre_layout)

        self.setCentralWidget(centre_widget)




        self.make_status_bar_tall_enough_to_contain_progress_bar()

        self.show()

        # Initialise tracks & draw here temporarily to prove everything works or not

        self._tracks = get_all_tracks()
        self._current_track = self._tracks["jyllandsringen_pro_cw"]


        self._track_painter = TrackPainter()
        from episode.episode_filter import EpisodeFilter
        self._episode_filter = EpisodeFilter()


        # Code that will move to the view menu etc.

        self._track_painter.set_waypoint_sizes_micro()
        self._track_painter.set_track_colour_blue()
        self._track_painter.set_grid_back()
        self._track_painter.set_waypoint_labels_on()
        self._track_painter.set_sectors_on()

        ## Code that will move to the analyzer

        self._current_track.configure_track_canvas(self.canvas)
        self._track_painter.draw(self.canvas, self._current_track, self._episode_filter)

        # self._current_track.draw_track_edges(self.canvas, track_grey)
        # self._current_track.draw_waypoints(self.canvas, track_grey, 2, 8)
        # self._current_track.draw_section_highlight(self.canvas, track_grey, 0, 20)
        # self._current_track.draw_starting_line(self.canvas, track_grey)
        # self._current_track.draw_sector_dividers(self.canvas, track_grey)
        # self._current_track.draw_waypoint_labels(self.canvas, track_grey, 9)
        # self._current_track.draw_grid(self.canvas, grid_grey)

    def set_busy_cursor(self):
        self.setCursor(Qt.CursorShape.WaitCursor)

    def set_normal_cursor(self):
        self.unsetCursor()

    def make_status_bar_tall_enough_to_contain_progress_bar(self):
        dummy_sizing_progress_bar = QProgressBar()
        self.statusBar().addPermanentWidget(dummy_sizing_progress_bar)
        h = self.statusBar().geometry().height()
        self.statusBar().removeWidget(dummy_sizing_progress_bar)
        self.statusBar().setMinimumHeight(h)

    def _action_open_file(self):
        dlg = OpenFileDialog(self, self._please_wait, self._current_track, self._config_manager.get_log_directory(), self._chosen_open_file_callback)
        if not dlg.exec():
            print("Cancelled dialog")
            return

        self.setWindowTitle(self._open_file_dialog_chosen_model_title)

        log = Log(self._config_manager.get_log_directory())
        log.load_all(self._open_file_dialog_chosen_files, self._please_wait, self._current_track,
                     self._config_manager.get_calculate_new_reward(),
                     self._config_manager.get_calculate_alternate_discount_factors())
        self._open_log_status.open_log(log, self._open_file_dialog_chosen_model_title)

    def _chosen_open_file_callback(self, file_names, model_title):
        self._open_file_dialog_chosen_files = file_names
        self._open_file_dialog_chosen_model_title = model_title

    def _action_file_info(self):
        log = self._open_log_status.get_log()
        print("DEBUG FILE INFO")
        print("Title / Model Name =", self._open_log_status.get_model_name())
        print("Log directory =", log.get_log_directory())
        print("Log filename(s) =", log.get_log_file_name())
        print("Log meta filename(s) =", log.get_meta_file_name())

    def _action_change_log_directory(self):
        new_directory = QFileDialog.getExistingDirectory(self, self._actions.change_log_directory.statusTip(), self._config_manager.get_log_directory())
        if new_directory != "":
            self._config_manager.set_log_directory(new_directory)
            # self.menu_bar.refresh()   # TODO - Equivalent in new UI is to be determined

    def _action_set_file_options(self):
        print("File Options - NOT IMPLEMENTED YET IN VERSION 4")

    def _action_exit(self):
        self.close()


if __name__ == '__main__':
    app = QApplication([])

    # app.setStyleSheet("QLabel { color: red }   QProgressBar::chunk { background-color: blue }")

    window = MainWindow()
    sys.exit(app.exec())
