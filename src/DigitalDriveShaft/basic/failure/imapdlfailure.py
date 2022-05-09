try:
    from ansys.mapdl.core import Mapdl

    class IMAPDLFailure:
        def add_to_mapdl(self, mapdl: Mapdl, mat_id: int):
            raise NotImplementedError
except ModuleNotFoundError:
    class IMAPDLFailure:
        pass

    class Mapdl:
        def fc(
                self,
                mat="",
                lab1="",
                lab2="",
                data1="",
                data2="",
                data3="",
                data4="",
                data5="",
                data6="",
                **kwargs,
        ):
            pass
