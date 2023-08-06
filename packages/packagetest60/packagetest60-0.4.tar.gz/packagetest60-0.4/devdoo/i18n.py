#!/usr/bin/env python
# -*- coding: utf-8 -*-

import i18n

name ='Israel'
i18n.set('locale', 'xs')
i18n.set('fallback', 'en')
i18n.load_path.append('./translations')
i18n.set('file_format', 'json')
print i18n.t('foo.NAME_NOT_VALID', name=name) # Hello world !
