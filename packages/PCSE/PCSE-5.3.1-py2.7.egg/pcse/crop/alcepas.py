# -*- coding: utf-8 -*-
# Copyright (c) 2004-2014 Alterra, Wageningen-UR
# Allard de Wit (allard.dewit@wur.nl), October 2017
"""Basic routines for ALCEPAS onion model
"""
from __future__ import print_function
from math import sqrt, exp, cos, pi
from collections import deque
from array import array

from ..traitlets import Instance, Float, AfgenTrait

from .assimilation import totass
from ..util import limit, astro, doy, daylength
from ..base_classes import ParamTemplate, StatesTemplate, RatesTemplate, SimulationObject
from ..decorators import prepare_rates, prepare_states
from .. import signals


class ALCEPAS_Respiration(SimulationObject):

    class Parameters(ParamTemplate):
        Q10 = Float()
        MSOTB = AfgenTrait()
        MLVTB = AfgenTrait()
        MRTTB = AfgenTrait()

    class RateVariables(RatesTemplate):
        MAINT = Float()

    def initialize(self, day, kiosk, parvalues):
        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk, publish="MAINT")

    @prepare_rates
    def __call__(self, day, drv):
        r = self.rates
        s = self.states
        k = self.kiosk
        p = self.params
        MAINSO = p.MSOTB(k.DVS)
        MAINLV = p.MLVTB(k.DVS)
        MAINRT = p.MRTIB(k.DVS)
        MAINTS = MAINLV * k.WLV + MAINRT * k.WRT + MAINSO * k.WSO

        TEFF = p.Q10 ** ((drv.TEMP - 20.) / 10.)
        MNDVS = 1.0
        MAINT = min(k.GPHOT, MAINTS * TEFF * MNDVS)


class ALCEPAS_Assimilation(SimulationObject):

    class Parameters(ParamTemplate):
        AMX = Float()
        EFF = Float()
        KDIF = Float()
        AMDVST = AfgenTrait()
        AMTMPT = AfgenTrait()

    class RateVariables(RatesTemplate):
        GPHOT = Float()

    def initialize(self, day, kiosk, parvalues):
        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk, publish="GPHOT")

    @prepare_rates
    def __call__(self, day, drv):
        r = self.rates
        s = self.states
        k = self.kiosk
        p = self.params

        a  = astro(day, drv.LAT, drv.IRRAD)
        AMDVS = p.AMDVST(k.DVS)
        AMTMP = p.AMTMPT(drv.DTEMP)
        AMAX = p.AMX * AMDVS * AMTMP
        DTGA = totass(a.DAYL, AMAX, p.EFF, k.LAI, p.KDIF, drv.IRRAD, a.DIFPP, a.DSINBE, a.SINLD, a.COSLD)
        r.GPHOT = DTGA * 30./44.
        return r.GPHOT


class ALCEPAS_partitioning(SimulationObject):
    class Parameters(ParamTemplate):
        FLVTB = AfgenTrait()
        FSHTB = AfgenTrait()

    class RateVariables(RatesTemplate):
        FSH = Float()
        FLV = Float()
        FSO = Float()
        FRT = Float()

    def initialize(self, day, kiosk, parvalues):
        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk, publish=["FSH","FLV","FRT","FSO"])

    @prepare_rates
    def __call__(self, day, drv):
        r = self.rates
        p = self.params
        k = self.kiosk
        r.FSH = p.FSHTB(k.DVS)
        r.FRT = 1. - r.FSH
        r.FLV = p.FLVTB(k.DVS)
        r.FSO = 1. - r.FLV


class ALCEPAS_phenology(SimulationObject):

    class Parameters(ParamTemplate):
        TBAS = Float()
        DAGTB = AfgenTrait()
        RVRTB = AfgenTrait()
        BOL50 = Float()
        FALL50= Float()

    class StateVariables(StatesTemplate):
        DVS = Float()
        BULBSUM = Float()
        BULB = Float()

    class RateVariables(RatesTemplate):
        DTDEV = Float()
        DAYFAC = Float()
        RFR = Float()
        RFRFAC = Float()
        DVR = Float()
        DTSUM = Float()

    def initialize(self, day, kiosk, parvalues):
        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk)
        self.states = self.StateVariables(kiosk, DVS=0., BULBSUM=0.,
                                          BULB=0., LAI=5., publish="DVS")
        pass

    @prepare_rates
    def calc_rates(self, day, drv):
        r = self.rates
        s = self.states
        k = self.kiosk
        p = self.params

        r.DTDEV = max(0., drv.TEMP - p.TBAS)
        if s.DVS < 1.0:
            DL = daylength(day, drv.LAT)
            r.DAYFAC = p.DAGTB(DL)
            r.RFR = exp(-0.222 * k.LAI)
            r.RFRFAC = p.RVRTB(r.RFR)
            r.DTSUM = r.DTDEV * r.DAYFAC * r.RFRFAC
            r.DVR = r.DTSUM/p.BOL50
        else:
            r.DTSUM = r.DTDEV
            r.DVR = r.DTSUM/p.FALL50

    @prepare_states
    def integrate(self, day, delt=1.0):
        s = self.states
        r = self.rates
        s.BULBSUM += r.DTSUM * delt
        s.DVS += r.DVR * delt
        BULB = 0.3 + 100.45 * (exp(-exp(-0.0293*(s.BULBSUM - 91.9))))
        s.BULB = limit(0., 100., BULB)

        if s.DVS > 2:
            self._send_signal(signal=signals.crop_finish, day=day,
                   finish_type="MATURITY", crop_delete=True)


class ALCEPAS_leaf_dynamics(SimulationObject):

    class StateVariables(StatesTemplate):
        LAI = Float

    def initialize(self, day, kiosk, parvalues):
        self.states = self.StateVariables(kiosk, LAI=1.0, publish="LAI")

    def calc_rates(self, day, drv):
        pass

    def integrate(self, day, delt=1.0):
        self.touch()


class ALCEPAS_Leaf_Dynamics(SimulationObject):
    """Leaf dynamics for the WOFOST crop model.

    Implementation of biomass partitioning to leaves, growth and senenscence
    of leaves. WOFOST keeps track of the biomass that has been partitioned to
    the leaves for each day (variable `LV`), which is called a leaf class).
    For each leaf class the leaf age (variable 'LVAGE') and specific leaf area
    (variable `SLA`) are also registered. Total living leaf biomass is
    calculated by summing the biomass values for all leaf classes. Similarly,
    leaf area is calculated by summing leaf biomass times specific leaf area
    (`LV` * `SLA`).

    Senescense of the leaves can occur as a result of physiological age,
    drought stress or self-shading.

    *Simulation parameters* (provide in cropdata dictionary)

    =======  ============================================= =======  ============
     Name     Description                                   Type     Unit
    =======  ============================================= =======  ============
    RGRLAI   Maximum relative increase in LAI.              SCr     ha ha-1 d-1
    SPAN     Life span of leaves growing at 35 Celsius      SCr     |d|
    TBASE    Lower threshold temp. for ageing of leaves     SCr     |C|
    PERDL    Max. relative death rate of leaves due to      SCr
             water stress
    TDWI     Initial total crop dry weight                  SCr     |kg ha-1|
    KDIFTB   Extinction coefficient for diffuse visible     TCr
             light as function of DVS
    SLATB    Specific leaf area as a function of DVS        TCr     |ha kg-1|
    =======  ============================================= =======  ============

    *State variables*

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    LV       Leaf biomass per leaf class                        N    |kg ha-1|
    SLA      Specific leaf area per leaf class                  N    |ha kg-1|
    LVAGE    Leaf age per leaf class                            N    |d|
    LVSUM    Sum of LV                                          N    |kg ha-1|
    LAIEM    LAI at emergence                                   N    -
    LASUM    Total leaf area as sum of LV*SLA,                  N    -
             not including stem and pod area                    N
    LAIEXP   LAI value under theoretical exponential growth     N    -
    LAIMAX   Maximum LAI reached during growth cycle            N    -
    LAI      Leaf area index, including stem and pod area       Y    -
    WLV      Dry weight of living leaves                        Y    |kg ha-1|
    DWLV     Dry weight of dead leaves                          N    |kg ha-1|
    TWLV     Dry weight of total leaves (living + dead)         Y    |kg ha-1|
    =======  ================================================= ==== ============


    *Rate variables*

    =======  ================================================= ==== ============
     Name     Description                                      Pbl      Unit
    =======  ================================================= ==== ============
    GRLV     Growth rate leaves                                 N   |kg ha-1 d-1|
    DSLV1    Death rate leaves due to water stress              N   |kg ha-1 d-1|
    DSLV2    Death rate leaves due to self-shading              N   |kg ha-1 d-1|
    DSLV3    Death rate leaves due to frost kill                N   |kg ha-1 d-1|
    DSLV     Maximum of DLSV1, DSLV2, DSLV3                     N   |kg ha-1 d-1|
    DALV     Death rate leaves due to aging.                    N   |kg ha-1 d-1|
    DRLV     Death rate leaves as a combination of DSLV and     N   |kg ha-1 d-1|
             DALV
    SLAT     Specific leaf area for current time step,          N   |ha kg-1|
             adjusted for source/sink limited leaf expansion
             rate.
    FYSAGE   Increase in physiological leaf age                 N   -
    GLAIEX   Sink-limited leaf expansion rate (exponential      N   |ha ha-1 d-1|
             curve)
    GLASOL   Source-limited leaf expansion rate (biomass        N   |ha ha-1 d-1|
             increase)
    =======  ================================================= ==== ============


    *External dependencies:*

    ======== ============================== =============================== ===========
     Name     Description                         Provided by               Unit
    ======== ============================== =============================== ===========
    DVS      Crop development stage         DVS_Phenology                    -
    FL       Fraction biomass to leaves     DVS_Partitioning                 -
    FR       Fraction biomass to roots      DVS_Partitioning                 -
    SAI      Stem area index                WOFOST_Stem_Dynamics             -
    PAI      Pod area index                 WOFOST_Storage_Organ_Dynamics    -
    TRA      Transpiration rate             Evapotranspiration              |cm day-1|
    TRAMX    Maximum transpiration rate     Evapotranspiration              |cm day-1|
    ADMI     Above-ground dry matter        CropSimulation                  |kg ha-1 d-1|
             increase
    RF_FROST Reduction factor frost kill    FROSTOL                          -
    ======== ============================== =============================== ===========
    """

    class Parameters(ParamTemplate):
        RGRLAI = Float(-99.)
        SPAN = Float(-99.)
        TBASE = Float(-99.)
        PERDL = Float(-99.)
        TDWI = Float(-99.)
        SLATB = AfgenTrait()
        KDIFTB = AfgenTrait()

    class StateVariables(StatesTemplate):
        LV = Instance(deque)
        SLA = Instance(deque)
        LVAGE = Instance(deque)
        LAIEM = Float(-99.)
        LASUM = Float(-99.)
        LAIEXP = Float(-99.)
        LAIMAX = Float(-99.)
        LAI = Float(-99.)
        WLV = Float(-99.)
        DWLV = Float(-99.)
        TWLV = Float(-99.)

    class RateVariables(RatesTemplate):
        GRLV = Float(-99.)
        DSLV1 = Float(-99.)
        DSLV2 = Float(-99.)
        DSLV3 = Float(-99.)
        DSLV = Float(-99.)
        DALV = Float(-99.)
        DRLV = Float(-99.)
        SLAT = Float(-99.)
        FYSAGE = Float(-99.)
        GLAIEX = Float(-99.)
        GLASOL = Float(-99.)

    def initialize(self, day, kiosk, parvalues):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE  instance
        :param parvalues: `ParameterProvider` object providing parameters as
                key/value pairs
        """

        self.kiosk = kiosk
        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk)

        # CALCULATE INITIAL STATE VARIABLES
        params = self.params
        FL = self.kiosk["FL"]
        FR = self.kiosk["FR"]
        DVS = self.kiosk["DVS"]

        # Initial leaf biomass
        WLV = (params.TDWI * (1 - FR)) * FL
        DWLV = 0.
        TWLV = WLV + DWLV

        # First leaf class (SLA, age and weight)
        SLA = deque([params.SLATB(DVS)])
        LVAGE = deque([0.])
        LV = deque([WLV])

        # Initial values for leaf area
        LAIEM = LV[0] * SLA[0]
        LASUM = LAIEM
        LAIEXP = LAIEM
        LAIMAX = LAIEM
        LAI = LASUM + self.kiosk["SAI"] + self.kiosk["PAI"]

        # Initialize StateVariables object
        self.states = self.StateVariables(kiosk, publish=["LAI", "TWLV", "WLV"],
                                          LV=LV, SLA=SLA, LVAGE=LVAGE, LAIEM=LAIEM,
                                          LASUM=LASUM, LAIEXP=LAIEXP, LAIMAX=LAIMAX,
                                          LAI=LAI, WLV=WLV, DWLV=DWLV, TWLV=TWLV)

    def _calc_LAI(self):
        # Total leaf area Index as sum of leaf, pod and stem area
        SAI = self.kiosk["SAI"]
        PAI = self.kiosk["PAI"]
        return self.states.LASUM + SAI + PAI

    @prepare_rates
    def calc_rates(self, day, drv):
        rates = self.rates
        states = self.states
        params = self.params

        # Growth rate leaves
        # weight of new leaves
        ADMI = self.kiosk["ADMI"]
        FL = self.kiosk["FL"]
        rates.GRLV = ADMI * FL

        # death of leaves due to water stress
        TRA = self.kiosk["TRA"]
        TRAMX = self.kiosk["TRAMX"]
        rates.DSLV1 = states.WLV * (1. - TRA / TRAMX) * params.PERDL

        # death due to self shading cause by high LAI
        DVS = self.kiosk["DVS"]
        LAICR = 3.2 / params.KDIFTB(DVS)
        rates.DSLV2 = states.WLV * limit(0., 0.03, 0.03 * (states.LAI - LAICR) / LAICR)

        # Death of leaves due to frost damage as determined by
        # Reduction Factor Frost "RF_FROST"
        if "RF_FROST" in self.kiosk:
            rates.DSLV3 = states.WLV * self.kiosk["RF_FROST"]
        else:
            rates.DSLV3 = 0.

        # leaf death equals maximum of water stress, shading and frost
        rates.DSLV = max(rates.DSLV1, rates.DSLV2, rates.DSLV3)

        # Determine how much leaf biomass classes have to die in states.LV,
        # given the a life span > SPAN, these classes will be accumulated
        # in DALV.
        # Note that the actual leaf death is imposed on the array LV during the
        # state integration step.
        DALV = 0.0
        for lv, lvage in zip(states.LV, states.LVAGE):
            if lvage > params.SPAN:
                DALV += lv
        rates.DALV = DALV

        # Total death rate leaves
        rates.DRLV = max(rates.DSLV, rates.DALV)

        # physiologic ageing of leaves per time step
        rates.FYSAGE = max(0., (drv.TEMP - params.TBASE) / (35. - params.TBASE))

        # specific leaf area of leaves per time step
        rates.SLAT = params.SLATB(DVS)

        # leaf area not to exceed exponential growth curve
        if (states.LAIEXP < 6.):
            DTEFF = max(0., drv.TEMP - params.TBASE)
            rates.GLAIEX = states.LAIEXP * params.RGRLAI * DTEFF
            # source-limited increase in leaf area
            rates.GLASOL = rates.GRLV * rates.SLAT
            # sink-limited increase in leaf area
            GLA = min(rates.GLAIEX, rates.GLASOL)
            # adjustment of specific leaf area of youngest leaf class
            if (rates.GRLV > 0.):
                rates.SLAT = GLA / rates.GRLV

    @prepare_states
    def integrate(self, day, delt=1.0):
        params = self.params
        rates = self.rates
        states = self.states

        # --------- leave death ---------
        tLV = array('d', states.LV)
        tSLA = array('d', states.SLA)
        tLVAGE = array('d', states.LVAGE)
        tDRLV = rates.DRLV

        # leaf death is imposed on leaves by removing leave classes from the
        # right side of the deque.
        for LVweigth in reversed(states.LV):
            if tDRLV > 0.:
                if tDRLV >= LVweigth:  # remove complete leaf class from deque
                    tDRLV -= LVweigth
                    tLV.pop()
                    tLVAGE.pop()
                    tSLA.pop()
                else:  # Decrease value of oldest (rightmost) leave class
                    tLV[-1] -= tDRLV
                    tDRLV = 0.
            else:
                break

        # Integration of physiological age
        tLVAGE = deque([age + rates.FYSAGE for age in tLVAGE])
        tLV = deque(tLV)
        tSLA = deque(tSLA)

        # --------- leave growth ---------
        # new leaves in class 1
        tLV.appendleft(rates.GRLV)
        tSLA.appendleft(rates.SLAT)
        tLVAGE.appendleft(0.)

        # calculation of new leaf area
        states.LASUM = sum([lv * sla for lv, sla in zip(tLV, tSLA)])
        states.LAI = self._calc_LAI()
        states.LAIMAX = max(states.LAI, states.LAIMAX)

        # exponential growth curve
        states.LAIEXP += rates.GLAIEX

        # Update leaf biomass states
        states.WLV = sum(tLV)
        states.DWLV += rates.DRLV
        states.TWLV = states.WLV + states.DWLV

        # Store final leaf biomass deques
        self.states.LV = tLV
        self.states.SLA = tSLA
        self.states.LVAGE = tLVAGE


class ALCEPAS(SimulationObject):
    LAI_dynamics = Instance(SimulationObject)
    phenology = Instance(SimulationObject)
    partitioning = Instance(SimulationObject)
    assimilation = Instance(SimulationObject)
    respiration = Instance(SimulationObject)

    class Parameters(ParamTemplate):
        ASRQSO = Float()
        ASRQRT = Float()
        ASRQLV = Float()

    class RateVariables(RatesTemplate):
        GTW = Float()
        GSH = Float()
        GSO = Float()
        GRT = Float()
        GLV = Float()

    class StateVariables(StatesTemplate):
        WLVG = Float()
        WLVD = Float()
        WSO = Float()
        WRT = Float()
        WLV = Float()
        TADRW = Float()

    def initialize(self, day, kiosk, parvalues):
        self.LAI_dynamics = ALCEPAS_leaf_dynamics(day, kiosk, parvalues)
        self.phenology = ALCEPAS_phenology(day, kiosk, parvalues)
        self.partitioning = ALCEPAS_partitioning(day, kiosk, parvalues)
        self.assimilation = ALCEPAS_Assimilation(day, kiosk, parvalues)
        self.respiration = ALCEPAS_Respiration(day, kiosk, parvalues)

    def calc_rates(self, day, drv):
        p = self.params
        k = self.kiosk
        r = self.rates
        s = self.states

        self.LAI_dynamics.calc_rates(day, drv)
        self.phenology.calc_rates(day, drv)
        self.partitioning(day, drv)
        GPHOT = self.assimilation(day, drv)
        MAINT = self.respiration(day, drv)

        # assimilate requirements for dry matter conversion (kgCH20 / kgDM)
        ASRQ = k.FSH * (p.ASRQLV * k.FLV + p.ASRQSO * k.FSO) + p.ASRQRT * k.FRT
        r.GTW = (GPHOT - MAINT) / ASRQ
        r.GSH = k.FSH * r.GTW
        r.GLV = k.FLV * r.GSH
        r.GSO = k.FSO * r.GSH
        r.GRT = k.FRT * r.GTW

    def integrate(self, day, delt=1.0):
        p = self.params
        k = self.kiosk
        r = self.rates
        s = self.states

        self.LAI_dynamics.integrate(day, delt)
        self.phenology.integrate(day, delt)

        s.WLVG += (r.GLV - r.DLV) * delt
        s.WLVD += r.DLV * delt
        s.WLV = s.WLVG + s.WLVD
        s.WSO += r.GSO * delt
        s.WRT += r.GRT * delt
        s.TADRW = s.WLV + s.WSO + s.WRT
