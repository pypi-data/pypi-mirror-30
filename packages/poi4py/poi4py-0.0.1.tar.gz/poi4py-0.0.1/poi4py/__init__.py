import os

import jpype


def start_jvm():
    java_library_path = f'{os.path.dirname(__file__)}/java/'
    classpath = os.pathsep.join(f'{java_library_path}/{lib}' for lib in [
        'poi-3.17.jar',
        'poi-excelant-3.17.jar',
        'poi-ooxml-3.17.jar',
        'poi-ooxml-schemas-3.17.jar',
        'poi-scratchpad-3.17.jar',
        'lib/commons-codec-1.10.jar',
        'lib/commons-collections4-4.1.jar',
        'lib/commons-logging-1.2.jar',
        'lib/log4j-1.2.17.jar',
        'ooxml-lib/xmlbeans-2.6.0.jar',
        'ooxml-lib/curvesapi-1.04.jar',
    ])

    jpype.startJVM(jpype.get_default_jvm_path(),
                   f'-Djava.class.path={classpath}',
                   '-Dfile.encoding=UTF8',
                   '-ea',
                   '-Xmx1024m')


def open_workbook(filename, password=None):
    from jpype import java
    return jpype.JPackage('org').apache.poi.ss.usermodel.WorkbookFactory.create(java.io.File(filename), password)


def shutdown_jvm():
    jpype.shutdownJVM()
