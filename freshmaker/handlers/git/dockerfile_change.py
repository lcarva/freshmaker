# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>

from freshmaker import log
from freshmaker.handlers import BaseHandler
from freshmaker.events import GitDockerfileChangeEvent


class GitDockerfileChangeHandler(BaseHandler):
    name = 'GitDockerfileChangeHandler'

    def can_handle(self, event):
        return isinstance(event, GitDockerfileChangeEvent)

    def handle(self, event):
        """Rebuild docker image"""
        import koji

        log.info('Start to rebuild docker image %s.', event.container)

        if not self.allow_build('image', event.container, event.branch):
            log.info("Skip rebuild of %s:%s as it's not allowed by configured whitelist/blacklist",
                     event.container, event.branch)
            return []

        try:
            task_id = self.build_container(event.container, event.branch, event.rev)

            if task_id is not None:
                self.record_build(event, event.container, 'image', task_id)

        except koji.krbV.Krb5Error as e:
            log.exception('Failed to login Koji via Kerberos using GSSAPI. %s', e.args[1])
        except:
            log.exception('Could not create task to build docker image %s', event.container)

        return []