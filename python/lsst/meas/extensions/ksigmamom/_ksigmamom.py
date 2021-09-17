__all__ = ("SingleFrameKSigmaMomFluxPlugin", "SingleFrameKSigmaMomFluxConfig",
           "ForcedKSigmaMomFluxPlugin", "ForcedKSigmaMomFluxConfig")

import logging
import lsst.meas.base as measBase
from lsst.meas.base.fluxUtilities import FluxResultKey
import lsst.pex.config as pexConfig

PLUGIN_NAME = "ext_ksigmamom_KSigmaMomFlux"


class BaseKSigmaMomFluxConfig(measBase.BaseMeasurementPluginConfig):
    """Configuration parameters for KSigma Moments (ksigmamom) plugin.
    """

    registerForApCorr = pexConfig.Field(
        dtype=bool,
        default=True,
        doc="Register measurements for aperture correction?",
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
        flagDefs = measBase.FlagDefinitionList()
        baseName = name
        doc = f"ksigmamom"
        FluxResultKey.addFields(schema, name=baseName, doc=doc)

        # Need to do flagDefs

        if config.registerForApCorr:
            measBase.addApCorrName(baseName)

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

    @classmethod
    def getExecutionOrder(cls):
        # Docstring inherited
        return cls.FLUX_ORDER

    def measure(self, measRecord, exposure):
        # Docstring inherited.
        # center = measRecord.getCentroid()
        import IPython
        IPython.embed()
        pass


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

    @classmethod
    def getExecutionOrder(cls):
        # Docstring inherited.
        return cls.FLUX_ORDER

    def measure(self, measRecord, exposure, refRecord, refWcs):
        # Docstring inherited.
        # wcs = exposure.getWcs()
        # center = wcs.skyToPixel(refWcs.pixelToSky(refRecord.getCentroid()))

        import IPython
        IPython.embed()
        pass
