__all__ = ("SingleFrameKSigmaMomFluxPlugin", "SingleFrameKSigmaMomFluxConfig",
           "ForcedKSigmaMomFluxPlugin", "ForcedKSigmaMomFluxConfig")

import lsst.meas.base as measBase

PLUGIN_NAME = "ext_ksigmamom_KSigmaMomFlux"


class BaseKSigmaMomFluxConfig(measBase.BaseMeasurementPluginConfig):
    """Configuration parameters for KSigma Momemnts (ksigmamom) plugin.
    """
    pass


class BaseKSigmaMomFluxMixin:
    """
    """
    pass


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
