# -*- coding: utf-8 -*-
# module moustache

import logging
import os
import tempfile

import uno

from moustache.OdtXmlBuilder import OdtXmlBuilder

log = logging.getLogger('moustache.FusionHelper')
log.setLevel(logging.INFO)


class FusionHelper:
    @staticmethod
    def create_uno_service(service_name):
        sm = uno.getComponentContext().ServiceManager
        return sm.createInstanceWithContext(service_name, uno.getComponentContext())

    @staticmethod
    def urlify(path):
        return uno.systemPathToFileUrl(os.path.realpath(path))

    def __init__(self, port, filepath):
        log.info("Init Office connection")
        # get the uno component context from the PyUNO runtime
        local_context = uno.getComponentContext()
        # create the UnoUrlResolver
        resolver = local_context.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_context)
        # connect to the running office
        self.ctx = resolver.resolve(
            "uno:socket,host=localhost,port={0};urp;StarOffice.ComponentContext".format(str(port)))
        smgr = self.ctx.ServiceManager
        # get the central desktop object
        self.desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", self.ctx)
        self.comp = self.desktop.loadComponentFromURL(self.urlify(filepath), "_blank", 0, ())
        # access the current writer document
        self.model = self.desktop.getCurrentComponent()
        self.document = self.model.getCurrentController().getFrame()
        self.dispatcher = self.create_uno_service("com.sun.star.frame.DispatchHelper")
        log.info("Office connection done")

    @staticmethod
    def create_property_value(name, value):
        prop = uno.createUnoStruct("com.sun.star.beans.PropertyValue")
        prop.Name = name
        prop.Value = value
        return prop

    def search_and_select(self, text):
        log.info("Searching %s" % text)
        properties = (
            self.create_property_value('SearchItem.SearchString', text),
        )
        self.dispatcher.executeDispatch(self.document, ".uno:ExecuteSearch", "", 0, properties)
        return not self.get_cursor().isCollapsed()

    def search_and_replace(self, text, replace):
        log.info("Replace %s with %s" % (text, replace))
        properties = (
            self.create_property_value('SearchItem.SearchString', text),
            self.create_property_value('SearchItem.ReplaceString', replace),
            self.create_property_value('SearchItem.Command', 3),
        )
        self.dispatcher.executeDispatch(self.document, ".uno:ExecuteSearch", "", 0, properties)

    def insert_odt(self, path):
        log.info("Insert ODT %s" % path)
        properties = (
            self.create_property_value('Name', self.urlify(path)),
        )
        self.dispatcher.executeDispatch(self.document, ".uno:InsertDoc", "", 0, properties)

    def insert_txt(self, txt):
        log.info("Insert TXT %s" % txt)
        properties = (
            self.create_property_value('Text', txt),
        )
        self.dispatcher.executeDispatch(self.document, ".uno:InsertText", "", 0, properties)

    def _file2istream(self, fbytes):
        istream = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.io.SequenceInputStream", self.ctx)
        istream.initialize((uno.ByteSequence(fbytes),))
        return istream

    def load_graphic_context(self, img_data):
        graphic_provider = self.ctx.ServiceManager.createInstanceWithContext("com.sun.star.graphic.GraphicProvider",
                                                                             self.ctx)
        properties = (
            self.create_property_value('InputStream', self._file2istream(img_data)),
        )
        return graphic_provider.queryGraphic(properties)

    def insert_pdf(self, filename, quality=150):
        log.info("Insert PDF %s in %d dpi" % (filename, quality))
        # Build a basic ODT from the PDF file
        odt_builder = OdtXmlBuilder(filename, quality)

        # load the file created to repair it
        log.info("Saving builded ODT file using uno")
        loaded_file = self.desktop.loadComponentFromURL(self.urlify(odt_builder.final_odt_path), "_blank", 0, ())
        if loaded_file is None:
            print("Can't insert %s" % filename)
        loaded_file.storeToURL(self.urlify("%s-OK.odt" % odt_builder.tmp_dir), ())
        # close the document
        loaded_file.dispose()
        log.info("Builded ODT file saved")

        # Reactivate template main document
        self.document.activate()

        self.insert_odt("%s-OK.odt" % odt_builder.tmp_dir)

        self._add_page_break_after("§§%s§§%d§§" % (odt_builder.basename, len(odt_builder.files_list)))

        #  Close odt_builder to remove all temporary files
        odt_builder.close()
        #  Remove the injected ODT
        os.remove("%s-OK.odt" % odt_builder.tmp_dir)

    def _add_page_break_after(self, insert_after):
        # Add a page break
        text = self.comp.Text
        cursor = self.get_cursor()
        # Search for the last occurence of the insert tag
        self.search_and_select(insert_after)
        # go down 1 time to keep the string
        cursor.goDown(1, False)
        # Add a manual break at the end of the "annexe"
        cursor.BreakType = uno.Enum("com.sun.star.style.BreakType", "PAGE_BEFORE")
        text.insertControlCharacter(cursor.End,
                                    uno.getConstantByName("com.sun.star.text.ControlCharacter.PARAGRAPH_BREAK"), 0)

    def insert_img(self, img_data):
        img = self.comp.createInstance('com.sun.star.text.TextGraphicObject')

        img.Graphic = self.load_graphic_context(img_data)
        img.Surround = uno.Enum("com.sun.star.text.WrapTextMode", "THROUGHT")
        img.Width = 21000
        img.Height = 29700

        text = self.comp.Text
        cursor = self.get_cursor()
        text.insertTextContent(cursor, img, False)

    def execute(self, cmd):
        log.info("Execute %s command" % cmd)
        self.dispatcher.executeDispatch(self.document, ".uno:{0}".format(cmd), "", 0, ())

    def get_cursor(self):
        return self.model.getCurrentController().getViewCursor()

    def convert_odt_to_pdf(self, path):
        temp_file_name = tempfile.NamedTemporaryFile(suffix=".pdf").name
        loaded_file = self.desktop.loadComponentFromURL(self.urlify(path), "_blank", 0, ())
        if loaded_file is None:
            print("Can't load %s file" % path)
        loaded_file.storeToURL(self.urlify(temp_file_name), (
            self.create_property_value("FilterName", "writer_pdf_Export"),
        ))

        # close the document
        loaded_file.dispose()
        log.info("ODT file converted to PDF")

        # Reactivate template main document
        self.document.activate()

        return temp_file_name

    def save_and_close(self, path, pdf=False):
        log.info("Saving %s file in %s format" % (path, "PDF" if pdf else "ODT"))
        args = (
            self.create_property_value("FilterName", "writer_pdf_Export"),
        ) if pdf else ()

        self.model.storeToURL(self.urlify(path), args)
        # close the document
        self.model.dispose()


# Pour exemple, le code suivant ajoute des annexes après avoir détécté le tag "ANNEXES" sur un document odt
if __name__ == '__main__':
    helper = FusionHelper(2002, "../test.odt")
    if helper.search_and_select("ANNEXES"):
        helper.insert_pdf("../ressource/exemple-001/annexes/annexe_pdf_1.pdf", quality=100)

    helper.save_and_close("../saved.odt")
