#!/bin/bash

mkdir -p scantest/guides
mkdir -p scantest/reference
echo -e "# Welcome\n\nThis is the main README.\n\nIt has five lines." > scantest/README.md
echo -e "# Install Guide\n\nStep 1: Download.\nStep 2: Install.\nStep 3: Verify." > scantest/guides/install.md
echo -e "# API Reference\n\nEndpoint: /users\nMethod: GET\nReturns: JSON array" > scantest/reference/api.md
echo -e "This is a plain text changelog." > scantest/changelog.txt
echo -e "# Old Notes\n\nThese are old." > scantest/reference/old-notes.md