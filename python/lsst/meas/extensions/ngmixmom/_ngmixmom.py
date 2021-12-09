__all__ = ("SingleFrameNgmixMomFluxPlugin", "SingleFrameNgmixMomFluxConfig",
           "ForcedNgmixMomFluxPlugin", "ForcedNgmixMomFluxConfig")

import numpy as np

import logging
import lsst.meas.base as measBase
from lsst.meas.base.fluxUtilities import FluxResultKey
import lsst.pex.config as pexConfig

from metadetect.lsst import measure as lsst_measure
from metadetect.lsst.util import get_mbexp
from ngmix import prepsfmom

PLUGIN_NAME = "ext_ngmixmom_NgmixMomFlux"


class BaseNgmixMomFluxConfig(measBase.BaseMeasurementPluginConfig):
    """Configuration parameters for KSigma Moments (ksigmamom) plugin.
    """

    registerForApCorr = pexConfig.Field(
        dtype=bool,
        default=True,
        doc="Register measurements for aperture correction?",
    )

    fwhm = pexConfig.Field(
        dtype=float,
        default=2.0,
        doc="Moment FWHM (arcseconds)",
    )

    # Update this to allow a list of moments...
    kernel = pexConfig.Field(
        dtype=str,
        default='pgauss',
        doc="Type of moment kernel (pgauss, ksigma).",
    )

    stampSize = pexConfig.Field(
        dtype=int,
        default=80,
        doc="Fitting stamp size (pixels)",
    )

    def getAllNgmixMomResultNames(self, name):
        """Generate base names for all the ngmix moment fields.

        There's just the one at the moment.
        """
        return [name]


class BaseNgmixMomFluxMixin:
    """Mixin base class for ngmix moment photometry.
    """
    ConfigClass = BaseNgmixMomFluxConfig
    hasLogName = True

    def __init__(self, config, name, schema, logName=None):
        # flagDefs = measBase.FlagDefinitionList()
        baseName = name
        doc = "ngmixmom fields"
        FluxResultKey.addFields(schema, name=baseName, doc=doc)

        # Need to do flagDefs

        if config.registerForApCorr:
            measBase.addApCorrName(baseName)

        self._failKey = schema.addField(name + '_flag', type="Flag", doc="Set for any fatal failure.")

        self.log = logging.getLogger(logName)


class SingleFrameNgmixMomFluxConfig(BaseNgmixMomFluxConfig,
                                    measBase.SingleFramePluginConfig):
    """Config for SingleFrameNgmixMomFluxConfig."""
    pass


@measBase.register(PLUGIN_NAME)
class SingleFrameNgmixMomFluxPlugin(BaseNgmixMomFluxMixin, measBase.SingleFramePlugin):
    """Ngmix Moments in single-frame mode.
    """
    ConfigClass = SingleFrameNgmixMomFluxConfig

    def __init__(self, config, name, schema, metadata, logName=None):
        BaseNgmixMomFluxMixin.__init__(self, config, name, schema, logName=logName)
        measBase.SingleFramePlugin.__init__(self, config, name, schema, metadata, logName=logName)

        self.fitter = prepsfmom.PrePSFMom(config.fwhm, config.kernel)
        self.fitter.kind = config.kernel

    @classmethod
    def getExecutionOrder(cls):
        # Docstring inherited
        return cls.FLUX_ORDER

    def measure(self, measRecord, exposure):
        # Docstring inherited.

        center = measRecord.getCentroid()

        coordIn = measRecord.getCoord()
        measRecord.setCoord(exposure.getWcs().pixelToSky(center))

        mbexp = get_mbexp([exposure])

        res = lsst_measure.measure(mbexp,
                                   exposure,
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
            measRecord[f'{self.name}_instFlux'] = res[f'{self.config.kernel}_band_flux']
            measRecord[f'{self.name}_instFluxErr'] = res[f'{self.config.kernel}_band_flux_err']
            if res['flags'] > 0:
                measRecord[f'{self.name}_flag'] = True


class ForcedNgmixMomFluxConfig(BaseNgmixMomFluxConfig, measBase.ForcedPluginConfig):
    """Config for ForcedNgmixMomFluxPlugin."""


@measBase.register(PLUGIN_NAME)
class ForcedNgmixMomFluxPlugin(BaseNgmixMomFluxMixin, measBase.ForcedPlugin):
    """NgmixMom Flux photometry in forced mode.
    """
    ConfigClass = ForcedNgmixMomFluxConfig

    def __init__(self, config, name, schemaMapper, metadata, logName=None):
        schema = schemaMapper.editOutputSchema()
        BaseNgmixMomFluxMixin.__init__(self, config, name, schema, logName=logName)
        measBase.ForcedPlugin.__init__(self, config, name, schemaMapper, metadata, logName=logName)

        self.fitter = prepsfmom.PrePSFMom(config.fwhm, config.kernel)
        self.fitter.kind = config.kernel

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

        mbexp = get_mbexp([exposure])

        res = lsst_measure.measure(mbexp,
                                   exposure,
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
            measRecord[f'{self.name}_instFlux'] = res[f'{self.config.kernel}_band_flux']
            measRecord[f'{self.name}_instFluxErr'] = res[f'{self.config.kernel}_band_flux_err']
            if res['flags'][0] > 0:
                measRecord[f'{self.name}_flag'] = True
