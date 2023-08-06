from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic
from flashtext import KeywordProcessor

export_etabs_window, etabs_base = uic.loadUiType('applications/cfactor/widgets/export_etabs.ui')

class ExportToEtabs(etabs_base, export_etabs_window):
    def __init__(self, building, parent=None):
        super(ExportToEtabs, self).__init__()
        self.setupUi(self)
        self.building = building
        self.template_button.clicked.connect(self.selectFile)
        self.output_button.clicked.connect(self.saveFile)

    def accept(self):
        story_e2k_text = self.story_e2k_text()
        template_e2k = self.template_path_line.text()
        output_e2k = self.output_path_line.text()
        keyword_dict = {
            story_e2k_text: ["$ STORIES - IN SEQUENCE FROM TOP"]
            }
        keyword_dict_earthquake = self._earthquake_data()
        keyword_dict.update(keyword_dict_earthquake)
        keyword_processor = KeywordProcessor()
        keyword_processor.add_keywords_from_dict(keyword_dict)
        with open(template_e2k, 'r') as input_file:
            lines = input_file.read()
            with open(output_e2k, 'w') as output_file:
                keywords_found = keyword_processor.replace_keywords(lines)
                output_file.write(keywords_found)
        etabs_base.accept(self)

    def _story_data(self):
        story_height = []
        if self.simple_story_radiobutton.isChecked():
            num_story = self.number_of_story_spinox.value()
            typical_height = self.typical_height_spinbox.value() * 1000
            buttom_height = self.buttom_height_spinbox.value() * 1000
            for story in range(num_story, 1, -1):
                story_height.append((f'Story{story}', int(typical_height)))
            story_height.append(('Story1', int(buttom_height)))

        elif self.custom_story_radiobutton.isChecked():
            # do something
            print("custom")
        self.top_story = story_height[0][0]
        self.bottom_story = story_height[-1][0]
        return story_height

    def story_e2k_text(self):
        story_data = self._story_data()
        storye2ktext = '$ STORIES - IN SEQUENCE FROM TOP\n'
        for story in story_data:
            storye2ktext += '  STORY "{}"  HEIGHT {}\n'.format(story[0], story[1])
        storye2ktext += '  STORY "Base"  ELEV 0'
        return storye2ktext

    def _earthquake_data(self):
        results = self.building.results
        ex, ey = results[1], results[2]
        kx, ky = self.building.kx, self.building.ky
        ex_drift, kx_drift = self.building.results_drift[1], self.building.kx_drift
        ey_drift, ky_drift = self.building.results_drift[2], self.building.ky_drift
        # self.lastDirectory = lastDirectory
        EX = f"SHEARCOEFF {ex:.5f}  HEIGHTEXPONENT {kx:.4f}"
        EY = f"SHEARCOEFF {ey:.4f}  HEIGHTEXPONENT {ky:.5f}"
        EXDRIFT = f"SHEARCOEFF {ex_drift:.6f}  HEIGHTEXPONENT {kx_drift:.7f}"
        EYDRIFT = f"SHEARCOEFF {ey_drift:.7f}  HEIGHTEXPONENT {ky_drift:.6f}"
        TOP_BOT = f'TOPSTORY "{self.top_story}"    BOTTOMSTORY "{self.bottom_story}"'

        keyword_dict = {
            EX: ["SHEARCOEFF EXALL  HEIGHTEXPONENT KXALL", "SHEARCOEFF EX  HEIGHTEXPONENT KX"],
            EY: ["SHEARCOEFF EYALL  HEIGHTEXPONENT KYALL", "SHEARCOEFF EY  HEIGHTEXPONENT KY"],
            EXDRIFT: ["SHEARCOEFF EXDRIFT  HEIGHTEXPONENT KXDRIFT"],
            EYDRIFT: ["SHEARCOEFF EYDRIFT  HEIGHTEXPONENT KYDRIFT"],
            TOP_BOT: ["TOPSTORY TOP    BOTTOMSTORY BOT"]
            }
        return keyword_dict

    def selectFile(self):
        self.template_path_line.setText(QFileDialog.getOpenFileName()[0])

    def saveFile(self):
        self.output_path_line.setText(QFileDialog.getSaveFileName()[0])

        

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    exp_et_w = ExportToEtabs()
    if exp_et_w.exec_():
        print(exp_et_w.number_of_story_spinox.value())
    sys.exit(app.exec_())
