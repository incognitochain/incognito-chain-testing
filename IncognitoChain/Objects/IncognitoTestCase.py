from IncognitoChain.Configs import config
from IncognitoChain.Objects.TestBedObject import TestBed

SUT = TestBed(config.test_bed)
SUT.precondition_check()
