try:
    import cv_parser
except ImportError as e:
    import sys
    sys.path.append("./src")

import cv_parser


skillCV1 = cv_parser.cvAnalizer('./src/upload/DummyCV1.pdf')
skillCV2 = cv_parser.cvAnalizer('./src/upload/DummyCV2.pdf')

assert skillCV1 == ['Java', 'Python', 'SQL', 'React']
assert skillCV2 == ['Skill set could not be extracted.']

print('Test complete. Test cases ran with no errors.')
