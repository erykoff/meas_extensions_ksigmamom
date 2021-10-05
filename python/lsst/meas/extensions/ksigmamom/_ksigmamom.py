__all__ = ("SingleFrameKSigmaMomFluxPlugin", "SingleFrameKSigmaMomFluxConfig",
           "ForcedKSigmaMomFluxPlugin", "ForcedKSigmaMomFluxConfig")

import numpy as np

import logging
import lsst.meas.base as measBase
from lsst.meas.base.fluxUtilities import FluxResultKey
import lsst.pex.config as pexConfig

from metadetect import lsst_measure
from ngmix import ksigmamom

PLUGIN_NAME = "ext_ksigmamom_KSigmaMomFlux"


class BaseKSigmaMomFluxConfig(measBase.BaseMeasurementPluginConfig):
    """Configuration parameters for KSigma Moments (ksigmamom) plugin.
    """

    registerForApCorr = pexConfig.Field(
        dtype=bool,
        default=True,
        doc="Register measurements for aperture correction?",
    )

    ksigmaFwhm = pexConfig.Field(
        dtype=float,
        default=2.0,
        doc="KSigma moment FWHM (arcseconds)",
    )

    stampSize = pexConfig.Field(
        dtype=int,
        default=80,
        doc="Fitting stamp size (pixels)",
    )

    def getAllKSigmaMomResultNames(self, name):
        """Generate base names for all the ksigmamom fields.

        There's just the one at the moment.
        """
        return [name]


class BaseKSigmaMomFluxMixin:
    """Mixin base class for ksigmamom photometry.
    """
    ConfigClass = BaseKSigmaMomFluxConfig
    hasLogName = True

    def __init__(self, config, name, schema, logName=None):
        # flagDefs = measBase.FlagDefinitionList()
        baseName = name
        doc = "ksigmamom fields"
        FluxResultKey.addFields(schema, name=baseName, doc=doc)

        # Need to do flagDefs

        if config.registerForApCorr:
            measBase.addApCorrName(baseName)

        self._failKey = schema.addField(name + '_flag', type="Flag", doc="Set for any fatal failure.")

        self.log = logging.getLogger(logName)


class SingleFrameKSigmaMomFluxConfig(BaseKSigmaMomFluxConfig,
                                     measBase.SingleFramePluginConfig):
    """Config for SingleFrameKSigmaMomFluxConfig."""
    pass


@measBase.register(PLUGIN_NAME)
class SingleFrameKSigmaMomFluxPlugin(BaseKSigmaMomFluxMixin, measBase.SingleFramePlugin):
    """KSigma Moments in single-frame mode.
    """
    ConfigClass = SingleFrameKSigmaMomFluxConfig

    def __init__(self, config, name, schema, metadata, logName=None):
        BaseKSigmaMomFluxMixin.__init__(self, config, name, schema, logName=logName)
        measBase.SingleFramePlugin.__init__(self, config, name, schema, metadata, logName=logName)

        self.fitter = ksigmamom.KSigmaMom(config.ksigmaFwhm)

    @classmethod
    def getExecutionOrder(cls):
        # Docstring inherited
        return cls.FLUX_ORDER

    def measure(self, measRecord, exposure):
        # Docstring inherited.

        center = measRecord.getCentroid()

        coordIn = measRecord.getCoord()
        measRecord.setCoord(exposure.getWcs().pixelToSky(center))
        res = lsst_measure.measure(exposure,
                                   [measRecord],
                                   self.fitter,
                                   self.config.stampSize)

        measRecord.setCoord(coordIn)

        if res is None:
            # No measurement could be made
            measRecord[f'{self.name}_instFlux'] = np.nan
            measRecord[f'{self.name}_instFluxErr'] = np.nan
            measRecord[f'{self.name}_flag'] = True
        else:
            measRecord[f'{self.name}_instFlux'] = res['ksigma_flux']
            measRecord[f'{self.name}_instFluxErr'] = res['ksigma_flux_err']
            if res['flags'] > 0:
                measRecord[f'{self.name}_flag'] = True


class ForcedKSigmaMomFluxConfig(BaseKSigmaMomFluxConfig, measBase.ForcedPluginConfig):
    """Config for ForcedKSigmaMomFluxPlugin."""


@measBase.register(PLUGIN_NAME)
class ForcedKSigmaMomFluxPlugin(BaseKSigmaMomFluxMixin, measBase.ForcedPlugin):
    """KSigmaMom Flux photometry in forced mode.
    """
    ConfigClass = ForcedKSigmaMomFluxConfig

    def __init__(self, config, name, schemaMapper, metadata, logName=None):
        schema = schemaMapper.editOutputSchema()
        BaseKSigmaMomFluxMixin.__init__(self, config, name, schema, logName=logName)
        measBase.ForcedPlugin.__init__(self, config, name, schemaMapper, metadata, logName=logName)

        self.fitter = ksigmamom.KSigmaMom(config.ksigmaFwhm)

    @classmethod
    def getExecutionOrder(cls):
        # Docstring inherited.
        return cls.FLUX_ORDER

    def measure(self, measRecord, exposure, refRecord, refWcs):
        # Docstring inherited.

        # The measRecord has the coordinate from the refRecord when
        # running in forced mode?  Let's be sure.
        coordIn = measRecord.getCoord()
        measRecord.setCoord(coordIn)

        res = lsst_measure.measure(exposure,
                                   [measRecord],
                                   self.fitter,
                                   self.config.stampSize)
        measRecord.setCoord(coordIn)

        if res is None:
            # No measurement could be made
            measRecord[f'{self.name}_instFlux'] = np.nan
            measRecord[f'{self.name}_instFluxErr'] = np.nan
            measRecord[f'{self.name}_flag'] = True
        else:
            measRecord[f'{self.name}_instFlux'] = res['ksigma_flux']
            measRecord[f'{self.name}_instFluxErr'] = res['ksigma_flux_err']
            if res['flags'][0] > 0:
                measRecord[f'{self.name}_flag'] = True
