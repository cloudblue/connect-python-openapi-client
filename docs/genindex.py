import json
import shutil
import os
from datetime import datetime

import pytz


BASE_URL = 'https://raw.githubusercontent.com/cloudblue/connect-python-openapi-client/docs/markdown'
DOCS_URL = f'{BASE_URL}/docs/_build/markdown'

PAGES = (
    ('README.md', 'Welcome'),
    ('guide.md', 'User guide'),
    ('reference.md', 'API reference'),
)


def gen_index():
    docs_dir = os.path.join(
        os.path.dirname(__file__),
        '_build',
        'markdown',
    )

    shutil.copy(
        os.path.join(os.path.dirname(__file__), '..', 'README.md'),
        os.path.join(docs_dir, 'README.md'),
    )

    data = {
        'generated': datetime.now(tz=pytz.utc).isoformat(),
        'pages': [],
    }

    for idx, page_info in enumerate(PAGES):
        filename, title = page_info
        shutil.move(
            os.path.join(docs_dir, filename),
            os.path.join(docs_dir, f'{idx:03d}_{filename}'),
        )
        data['pages'].append(
            {
                'name': title,
                'category': title,
                'file': filename,
                'idx': str(idx),
                'outputFileName': f'{idx:03d}_{filename}',
                'url': f'{DOCS_URL}/{idx:03d}_{filename}',
            },
        )

    output_file = os.path.join(docs_dir, 'report.json')
    json.dump(data, open(output_file, 'w'), indent=2)

    print('documentation index generated')


if __name__ == '__main__':
    gen_index()
