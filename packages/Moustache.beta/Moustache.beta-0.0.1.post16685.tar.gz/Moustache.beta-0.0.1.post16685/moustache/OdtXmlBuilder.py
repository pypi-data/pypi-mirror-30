# -*- coding: utf-8 -*-
# module moustache

import os
import shutil
import uuid
import xml.etree.ElementTree
import zipfile
import logging
from subprocess import Popen, DEVNULL

from PIL import Image

log = logging.getLogger('moustache.OdtXmlBuilder')
log.setLevel(logging.INFO)

"""
Class to build an ODT file from PDF
It :
- Copy "minimal_odt" model to /tmp directory
- Extract PDF to pages with "pdftocairo" util (poppler-utils)
- Add images entries to ODT manifest
- Add XML elements to content
- Zip the all thing
"""


class OdtXmlBuilder:
    def __init__(self, filename, quality):
        log.info("Building XML ODT from PDF")
        # Init vars
        self._id = str(uuid.uuid4())
        self._quality = quality
        self._pages_layout = {}

        self.tmp_dir = "/tmp/%s" % str(self._id)
        # Copy basic ODT tree to tmp file
        shutil.copytree("minimal_odt", self.tmp_dir, ignore=shutil.ignore_patterns(".*", ))

        # get file basename
        self._basename = os.path.basename(filename)

        log.info("Begin convert PDF to images")
        # Generate all images
        Popen([
            'pdftocairo',
            '-jpeg',
            '-r',
            str(quality),
            filename,
            "%s/Pictures/%s" % (self.tmp_dir, str(uuid.uuid4().hex)),
        ], stdout=DEVNULL).communicate()

        # List files and ignore hidden files, just in case
        self._files_list = os.listdir("%s/Pictures" % self.tmp_dir)
        # Sort alpha
        self._files_list.sort()

        log.info("Build final XML")
        # Prepare office namespace
        self._init_xml_namespace()
        # Build manifest.xml file
        self._build_manifest()
        # Build content.xml file
        self._build_content_and_styles()
        # Zip final file
        self.final_odt_path = "%s.odt" % self.tmp_dir
        self._zipdir()

    """
    Init XML namespace, mandatory for python ElementTree search to work
    """

    @staticmethod
    def _init_xml_namespace():
        # Prepare libreoffice namespaces
        xml.etree.ElementTree.register_namespace("manifest", "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0")
        xml.etree.ElementTree.register_namespace("office", "urn:oasis:names:tc:opendocument:xmlns:office:1.0")
        xml.etree.ElementTree.register_namespace("style", "urn:oasis:names:tc:opendocument:xmlns:style:1.0")
        xml.etree.ElementTree.register_namespace("text", "urn:oasis:names:tc:opendocument:xmlns:text:1.0")
        xml.etree.ElementTree.register_namespace("draw", "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0")
        xml.etree.ElementTree.register_namespace("fo", "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0")
        xml.etree.ElementTree.register_namespace("xlink", "http://www.w3.org/1999/xlink")
        xml.etree.ElementTree.register_namespace("svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0")
        xml.etree.ElementTree.register_namespace("form", "urn:oasis:names:tc:opendocument:xmlns:form:1.0")
        xml.etree.ElementTree.register_namespace("officeooo", "http://openoffice.org/2009/office")

    """
    Build the manifest.xml with "Pictures" entries from the PDF
    """

    def _build_manifest(self):
        # Edit manifest.xml file
        manifest_path = '%s/META-INF/manifest.xml' % self.tmp_dir
        manifest = xml.etree.ElementTree.parse(manifest_path)

        for index, filename in enumerate(self._files_list):
            new_tag = xml.etree.ElementTree.SubElement(manifest.getroot(), 'manifest:file-entry')
            new_tag.attrib['manifest:full-path'] = "Pictures/%s" % filename
            new_tag.attrib['manifest:media-type'] = "image/jpeg"

        manifest.write(manifest_path)

    """
    Build the content.xml with custom elements (jump page and full page image)
    """

    def _build_content_and_styles(self):
        content_path = '%s/content.xml' % self.tmp_dir
        content = xml.etree.ElementTree.parse(content_path)
        self._content_root = content.getroot()

        styles_path = '%s/styles.xml' % self.tmp_dir
        styles = xml.etree.ElementTree.parse(styles_path)
        self._styles_root = styles.getroot()

        office_ns = {"office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0"}

        # Set missing namespace -> mandatory because ET removes it if not defined here !
        self._content_root.set("xmlns:svg", "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0")
        self._content_root.set("xmlns:xlink", "http://www.w3.org/1999/xlink")
        self._styles_root.set("xmlns:officeooo", "http://openoffice.org/2009/office")

        office_text = self._content_root.find("office:body", office_ns).find("office:text", office_ns)
        # Insert all content here

        for index, filename in enumerate(self._files_list):
            im = Image.open("%s/Pictures/%s" % (self.tmp_dir, filename))
            width, height = im.size

            size_tuple = (round(254 * width / self._quality / 100, 3), round(254 * height / self._quality / 100, 3))

            if size_tuple not in self._pages_layout:
                self._pages_layout[size_tuple] = self._build_style(size_tuple)

            self._insert_image_element(
                index,
                filename,
                office_text,
                size_tuple,
                self._pages_layout[size_tuple])

        # Save content
        content.write(content_path, encoding="UTF-8")
        # Save styles
        styles.write(styles_path, encoding="UTF-8")

    def _build_style(self, size):
        stylename = "%dx%d" % (size[0], size[1])

        office_ns = {"office": "urn:oasis:names:tc:opendocument:xmlns:office:1.0"}
        office_auto_styles = self._styles_root.find("office:automatic-styles", office_ns)

        page_layout_tag = xml.etree.ElementTree.SubElement(office_auto_styles, 'style:page-layout')
        page_layout_tag.attrib['style:name'] = "%s-layout" % stylename

        page_layout_properties_tag = xml.etree.ElementTree.SubElement(page_layout_tag, 'style:page-layout-properties')
        page_layout_properties_tag.attrib['fo:page-width'] = "%dcm" % size[0]
        page_layout_properties_tag.attrib['fo:page-height'] = "%dcm" % size[1]

        office_master_styles = self._styles_root.find("office:master-styles", office_ns)

        master_page_tag = xml.etree.ElementTree.SubElement(office_master_styles, 'style:master-page')
        master_page_tag.attrib['style:name'] = "%s-style" % stylename
        master_page_tag.attrib['style:page-layout-name'] = "%s-layout" % stylename

        office_auto_styles_content = self._content_root.find("office:automatic-styles", office_ns)

        style_tag = xml.etree.ElementTree.SubElement(office_auto_styles_content, 'style:style')
        style_tag.attrib['style:name'] = "%s-paragraph" % stylename
        style_tag.attrib['style:family'] = "paragraph"
        style_tag.attrib['style:parent-style-name'] = "Standard_import"
        style_tag.attrib['style:master-page-name'] = "%s-style" % stylename

        text_properties_tag = xml.etree.ElementTree.SubElement(style_tag, 'style:text-properties')
        text_properties_tag.attrib['officeooo:rsid'] = "0015024c"
        text_properties_tag.attrib['officeooo:paragraph-rsid'] = "0015024c"

        return "%s-paragraph" % stylename

    """
    Insert each Pictures in content.xml
    """

    def _insert_image_element(self, index, filename, office_text, size, style):
        p_elem = xml.etree.ElementTree.SubElement(office_text, 'text:p')
        p_elem.attrib['text:style-name'] = style

        frame_elem = xml.etree.ElementTree.SubElement(p_elem, 'draw:frame')
        frame_elem.attrib['draw:style-name'] = "fr1"
        frame_elem.attrib['draw:name'] = "Image%d" % index
        frame_elem.attrib['text:anchor-type'] = "paragraph"
        frame_elem.attrib['svg:width'] = "%dcm" % (size[0])
        frame_elem.attrib['svg:height'] = "%dcm" % (size[1])
        frame_elem.attrib['draw:z-index'] = "0"

        image_elem = xml.etree.ElementTree.SubElement(frame_elem, 'draw:image')
        image_elem.attrib['xlink:href'] = "Pictures/%s" % filename
        image_elem.attrib['xlink:type'] = "simple"
        image_elem.attrib['xlink:show'] = "embed"
        image_elem.attrib['xlink:actuate'] = "onLoad"

        frame_elem.tail = "§§%s§§%d§§" % (self._basename, index)

    """
    Zip the whole directory to an odt file
    """

    def _zipdir(self):
        assert os.path.isdir(self.tmp_dir)
        from contextlib import closing
        with closing(zipfile.ZipFile(self.final_odt_path, "w", zipfile.ZIP_STORED)) as z:
            for root, dirs, files in os.walk(self.tmp_dir):
                for fn in files:
                    absfn = os.path.join(root, fn)
                    zfn = absfn[len(self.tmp_dir) + len(os.sep):]
                    z.write(absfn, zfn)

    """
    Remove all generated documents
    """

    def close(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)
        os.remove(self.final_odt_path)
