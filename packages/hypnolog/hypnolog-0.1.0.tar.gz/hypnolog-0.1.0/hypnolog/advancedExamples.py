# import Hypnolog as HL
import hypnolog as HL

# Hypnolog python advanced usage examples:

# == error handling ==
def customHypnologErrorHandler(e):
    print('Error while logging with Hypnolog:\n', e);

# == initializations ==
HL.initialize(
        host='localhost',
        port=7001,
        errorHandler=customHypnologErrorHandler);

