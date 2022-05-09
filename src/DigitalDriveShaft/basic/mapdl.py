try:
    from ansys.mapdl.core import Mapdl

except ModuleNotFoundError:
    # Placeholder
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

        def mp(self, lab="", mat="", c0="", c1="", c2="", c3="", c4="", **kwargs):
            pass

        def tb(
                self,
                lab="",
                mat="",
                ntemp="",
                npts="",
                tbopt="",
                eosopt="",
                funcname="",
                **kwargs
        ):
            pass

        def tbtemp(self, temp="", kmod="", **kwargs):
            pass

        def tbdata(self, stloc="", c1="", c2="", c3="", c4="", c5="", c6="", **kwargs):
            pass

        def mpdata(
                self,
                lab="",
                mat="",
                sloc="",
                c1="",
                c2="",
                c3="",
                c4="",
                c5="",
                c6="",
                **kwargs,
        ):
            pass