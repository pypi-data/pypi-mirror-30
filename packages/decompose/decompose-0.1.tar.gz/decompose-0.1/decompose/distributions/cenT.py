from typing import Tuple, Dict, Type
import tensorflow as tf
from tensorflow import Tensor
import numpy as np

from decompose.distributions.distribution import DrawType, UpdateType
from decompose.distributions.distribution import Distribution
from decompose.distributions.t import T
from decompose.distributions.distribution import parameterProperty
from decompose.distributions.algorithms import Algorithms
from decompose.distributions.cenTAlgorithms import CenTAlgorithms


class CenT(T):
    def __init__(self,
                 Psi: Tensor = tf.constant([1.]),
                 nu: Tensor = tf.constant([1.]),
                 tau: Tensor = tf.constant([1.]),
                 name: str = "NA",
                 algorithms: Type[Algorithms] = CenTAlgorithms,
                 drawType: DrawType = DrawType.SAMPLE,
                 updateType: UpdateType = UpdateType.ALL,
                 persistent: bool = True) -> None:
        Distribution.__init__(self,
                              shape=Psi.shape,
                              latentShape=(),
                              name=name,
                              drawType=drawType,
                              dtype=Psi.dtype,
                              updateType=updateType,
                              persistent=persistent,
                              algorithms=algorithms)
        self._init({"Psi": Psi,
                    "nu": nu,
                    "tau": tau})

    @staticmethod
    def initializers(shape: Tuple[int, ...] = (1,),
                     latentShape: Tuple[int, ...] = (1000,),
                     dtype: np.dtype = np.float32) -> Dict[str, Tensor]:
        initializers = {
            "Psi": tf.constant(np.random.exponential(size=shape), dtype=dtype),
            "nu": tf.constant(np.random.exponential(size=shape), dtype=dtype),
            "tau": tf.constant(np.random.exponential(size=latentShape + shape),
                               dtype=dtype)
        }  # type: Dict[str, Tensor]
        return(initializers)

    @parameterProperty
    def mu(self) -> Tensor:
        return(tf.zeros_like(self.Psi))
