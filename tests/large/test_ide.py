# -*- coding: utf-8 -*-
# Copyright (C) 2014 Canonical
#
# Authors:
#  Didier Roche
#  Tin Tvrtković
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; version 3.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

"""Tests for the IDE category"""
import logging
import platform
import subprocess
import os
from tests.large import LargeFrameworkTests
from tests.tools import UMAKE, spawn_process

logger = logging.getLogger(__name__)


class EclipseJavaIDETests(LargeFrameworkTests):
    """The Eclipse distribution from the IDE collection."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "eclipse")
        self.desktop_filename = "eclipse-java.desktop"
        self.command_args = f'{UMAKE} ide eclipse'
        self.name = "Eclipse"

    @property
    def arch_option(self):
        """we return the expected arch call on command line"""
        return platform.machine()

    def test_default_eclipse_ide_install(self):
        """Install eclipse from scratch test case"""
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

        # on 64 bits, there is a java subprocess, we kill that one with SIGKILL (eclipse isn't reliable on SIGTERM)
        if self.arch_option == "x86_64":
            self.check_and_kill_process(["java", self.arch_option, self.installed_path],
                                        wait_before=self.TIMEOUT_START, send_sigkill=True)
        else:
            self.check_and_kill_process([self.exec_path],
                                        wait_before=self.TIMEOUT_START, send_sigkill=True)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"{self.name} is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()


class EclipseJEEIDETests(EclipseJavaIDETests):
    """The Eclipse distribution from the IDE collection."""

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "eclipse-jee")
        self.desktop_filename = "eclipse-jee.desktop"
        self.command_args = f'{UMAKE} ide eclipse-jee'
        self.name = "Eclipse JEE"


class EclipsePHPIDETests(EclipseJavaIDETests):
    """The Eclipse distribution from the IDE collection."""

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "eclipse-php")
        self.desktop_filename = "eclipse-php.desktop"
        self.command_args = f'{UMAKE} ide eclipse-php'
        self.name = "Eclipse PHP"


class EclipseCPPIDETests(EclipseJavaIDETests):
    """The Eclipse distribution from the IDE collection."""

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "eclipse-cpp")
        self.desktop_filename = "eclipse-cpp.desktop"
        self.command_args = f'{UMAKE} ide eclipse-cpp'
        self.name = "Eclipse CPP"


class IdeaIDETests(LargeFrameworkTests):
    """IntelliJ Idea from the IDE collection."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "idea")
        self.desktop_filename = 'jetbrains-idea-ce.desktop'
        self.command_args = f'{UMAKE} ide idea'
        self.name = 'Idea'

    def test_default_install(self):
        """Install from scratch test case"""
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        result = self.return_and_wait_expect(["ERROR: No Stable version available.",
                                              "Installation done"], timeout=self.TIMEOUT_INSTALL_PROGRESS)
        if result == 0:
            self.assertTrue(self.name == 'GoLand')
        elif result == 1:
            # we have an installed launcher, added to the launcher and an icon file
            self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
            self.assert_exec_exists()
            self.assert_icon_exists()
            self.assert_exec_link_exists()

            # launch it, send SIGTERM and check that it exits fine
            proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)

            self.check_and_kill_process(["java", self.installed_path], wait_before=self.TIMEOUT_START)
            proc.communicate()
            proc.wait(self.TIMEOUT_STOP)

            # ensure that it's detected as installed:
            self.child = spawn_process(self.command(self.command_args))
            self.expect_and_no_warn(f"{self.name} is already installed.*\[.*\] ")
            self.child.sendline()
            self.wait_and_close()

    def test_eap_install(self):
        self.installed_path += '-eap'
        self.desktop_filename = self.desktop_filename.replace('.desktop', '-eap.desktop')
        self.command_args += ' --eap'
        self.name += ' EAP'

        self.child = spawn_process(self.command(self.command_args))
        result = self.return_and_wait_expect(
            [
                r"ERROR: No EAP version available.*\[.*\]",
                f"Choose installation path: {self.installed_path}",
            ]
        )
        if result == 1:
            self.child.sendline("")
            self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
            self.wait_and_close()

            # we have an installed launcher, added to the launcher and an icon file
            self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
            self.assert_exec_exists()
            self.assert_icon_exists()
            self.assert_exec_link_exists()

            # launch it, send SIGTERM and check that it exits fine
            proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)

            self.check_and_kill_process(["java", self.installed_path], wait_before=self.TIMEOUT_START)
            proc.communicate()
            proc.wait(self.TIMEOUT_STOP)

            # ensure that it's detected as installed:
            self.child = spawn_process(self.command(self.command_args))
            self.expect_and_no_warn(f"{self.name} is already installed.*\[.*\] ")
            self.child.sendline()
            self.wait_and_close()


class IdeaUltimateIDETests(IdeaIDETests):
    """IntelliJ Idea Ultimate from the IDE collection."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "idea-ultimate")
        self.desktop_filename = 'jetbrains-idea.desktop'
        self.command_args = f'{UMAKE} ide idea-ultimate'
        self.name = 'Idea Ultimate'


class PyCharmIDETests(IdeaIDETests):
    """PyCharm from the IDE collection."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "pycharm")
        self.desktop_filename = 'jetbrains-pycharm-ce.desktop'
        self.command_args = f'{UMAKE} ide pycharm'
        self.name = 'PyCharm'


class PyCharmEducationalIDETests(IdeaIDETests):
    """PyCharm Educational from the IDE collection."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "pycharm-educational")
        self.desktop_filename = 'jetbrains-pycharm-edu.desktop'
        self.command_args = f'{UMAKE} ide pycharm-educational'
        self.name = 'PyCharm Educational'


class PyCharmProfessionalIDETests(IdeaIDETests):
    """PyCharm Professional from the IDE collection."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "pycharm-professional")
        self.desktop_filename = 'jetbrains-pycharm.desktop'
        self.command_args = f'{UMAKE} ide pycharm-professional'
        self.name = 'PyCharm Professional'


class RubyMineIDETests(IdeaIDETests):
    """RubyMine from the IDE collection."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "rubymine")
        self.desktop_filename = 'jetbrains-rubymine.desktop'
        self.command_args = f'{UMAKE} ide rubymine'
        self.name = 'RubyMine'


class WebStormIDETests(IdeaIDETests):
    """WebStorm from the IDE collection."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "webstorm")
        self.desktop_filename = 'jetbrains-webstorm.desktop'
        self.command_args = f'{UMAKE} ide webstorm'
        self.name = 'WebStorm'


class PhpStormIDETests(IdeaIDETests):
    """PhpStorm from the IDE collection."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "phpstorm")
        self.desktop_filename = 'jetbrains-phpstorm.desktop'
        self.command_args = f'{UMAKE} ide phpstorm'
        self.name = 'PhpStorm'


class CLionIDETests(IdeaIDETests):
    """CLion test from the IDE collection"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "clion")
        self.desktop_filename = 'jetbrains-clion.desktop'
        self.command_args = f'{UMAKE} ide clion'
        self.name = 'CLion'


class DataGripIDETests(IdeaIDETests):
    """Datagrip test from the IDE collection"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "datagrip")
        self.desktop_filename = 'jetbrains-datagrip.desktop'
        self.command_args = f'{UMAKE} ide datagrip'
        self.name = 'DataGrip'


class GoLandIDETests(IdeaIDETests):
    """GoLand test from the IDE collection"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "goland")
        self.desktop_filename = 'jetbrains-goland.desktop'
        self.command_args = f'{UMAKE} ide goland'
        self.name = 'GoLand'


class RiderIDETests(IdeaIDETests):
    """Rider from the IDE collection."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "rider")
        self.desktop_filename = 'jetbrains-rider.desktop'
        self.command_args = f'{UMAKE} ide rider'
        self.name = 'Rider'


class NetBeansTests(LargeFrameworkTests):
    """Tests for the Netbeans installer."""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "netbeans")
        self.desktop_filename = "netbeans.desktop"

    def test_default_install(self):
        """Install from scratch test case"""
        self.child = spawn_process(self.command(f'{UMAKE} ide netbeans'))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        logger.info("Installed, running...")

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

        self.check_and_kill_process(["java", self.installed_path], wait_before=self.TIMEOUT_START)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(f'{UMAKE} ide netbeans'))
        self.expect_and_no_warn(r"Netbeans is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()


class VisualStudioCodeTests(LargeFrameworkTests):
    """Tests for Visual Studio Code"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 20
    TIMEOUT_STOP = 20

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "visual-studio-code")
        self.desktop_filename = "visual-studio-code.desktop"
        self.command_args = f'{UMAKE} ide visual-studio-code'
        self.name = 'Visual Studio Code'

    def test_default_install(self):
        """Install visual studio from scratch test case"""

        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"\[I Accept.*\]")  # ensure we have a license question
        self.child.sendline("a")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

        self.check_and_kill_process([os.path.join(self.installed_path, 'code')],
                                    wait_before=self.TIMEOUT_START, send_sigkill=True)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(r"Visual Studio Code is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()

    def test_insiders_install(self):
        """Install visual studio insiders"""

        self.installed_path += '-insiders'
        self.desktop_filename = self.desktop_filename.replace('.desktop', '-insiders.desktop')
        self.command_args += ' --insiders'
        self.name += ' Insiders'

        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"\[I Accept.*\]")  # ensure we have a license question
        self.child.sendline("a")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

        self.check_and_kill_process([os.path.join(self.installed_path, 'code-insiders')],
                                    wait_before=self.TIMEOUT_START, send_sigkill=True)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(r"Visual Studio Code Insiders is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()


class LightTableTests(LargeFrameworkTests):
    """Tests for LightTable"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 20
    TIMEOUT_STOP = 20

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "lighttable")
        self.desktop_filename = "lighttable.desktop"
        self.command_args = f'{UMAKE} ide lighttable'

    def test_default_install(self):
        """Install LightTable from scratch test case"""

        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

        self.check_and_kill_process(["LightTable", self.installed_path],
                                    wait_before=self.TIMEOUT_START, send_sigkill=True)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(r"LightTable is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()


class DBeaverTests(LargeFrameworkTests):
    """Tests for DBeaver"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 20
    TIMEOUT_STOP = 20

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "dbeaver")
        self.desktop_filename = "dbeaver.desktop"
        self.command_args = f'{UMAKE} ide dbeaver'
        self.name = "DBeaver"

    @property
    def arch_option(self):
        """we return the expected arch call on command line"""
        return platform.machine()

    def test_default_install(self):
        """Install DBeaver from scratch test case"""

        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

        # on 64 bits, there is a java subprocess, we kill that one with SIGKILL (eclipse isn't reliable on SIGTERM)
        if self.arch_option == "x86_64":
            self.check_and_kill_process(["java", self.arch_option, self.installed_path],
                                        wait_before=self.TIMEOUT_START, send_sigkill=True)
        else:
            self.check_and_kill_process([self.exec_path],
                                        wait_before=self.TIMEOUT_START, send_sigkill=True)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"{self.name} is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()


class SpringToolsSuiteTests(LargeFrameworkTests):
    """Tests for Spring Tools Suite"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 60
    TIMEOUT_STOP = 60

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "spring-tools-suite")
        self.desktop_filename = "STS.desktop"
        self.command_args = f'{UMAKE} ide spring-tools-suite'
        self.name = 'Spring Tools Suite'

    @property
    def arch_option(self):
        """we return the expected arch call on command line"""
        return platform.machine()

    def test_default_install(self):
        """Install STS from scratch test case"""
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

        # on 64 bits, there is a java subprocess, we kill that one with SIGKILL (eclipse isn't reliable on SIGTERM)
        if self.arch_option == "x86_64":
            self.check_and_kill_process(["java", self.arch_option, self.installed_path],
                                        wait_before=self.TIMEOUT_START, send_sigkill=True)
        else:
            self.check_and_kill_process([self.exec_path],
                                        wait_before=self.TIMEOUT_START, send_sigkill=True)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"{self.name} is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()


class RStudioTests(LargeFrameworkTests):
    """Tests for RStudio"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 20
    TIMEOUT_STOP = 20

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "rstudio")
        self.desktop_filename = "rstudio.desktop"
        self.command_args = f'{UMAKE} ide rstudio'

    def test_default_install(self):
        """Install Sublime Text from scratch test case"""

        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        self.check_and_kill_process([self.exec_path], wait_before=self.TIMEOUT_START, send_sigkill=True)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(r"RStudio is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()


class SublimeTextTests(LargeFrameworkTests):
    """Tests for Sublime Text"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 20
    TIMEOUT_STOP = 20

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "sublime-text")
        self.desktop_filename = "sublime-text.desktop"
        self.command_args = f'{UMAKE} ide sublime-text'

    def test_default_install(self):
        """Install Sublime Text from scratch test case"""

        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        self.check_and_kill_process([self.exec_path], wait_before=self.TIMEOUT_START, send_sigkill=True)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(r"Sublime Text is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()


class ProcessingTests(LargeFrameworkTests):
    """Tests for Processing"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 20
    TIMEOUT_STOP = 20

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "processing")
        self.desktop_filename = "processing.desktop"
        self.command_args = f'{UMAKE} ide processing'

    @property
    def arch_option(self):
        """we return the expected arch call on command line"""
        return platform.machine()

    def test_default_install(self):
        """Install Processing from scratch test case"""

        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

        self.check_and_kill_process(["java", "processing.app.Base"], wait_before=self.TIMEOUT_START)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(r"Processing is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()


class LiteIDETests(LargeFrameworkTests):
    """Tests for LiteIDE"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 20
    TIMEOUT_STOP = 20

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "liteide")
        self.desktop_filename = "liteide.desktop"
        self.command_args = f'{UMAKE} ide liteide'

    @property
    def arch_option(self):
        """we return the expected arch call on command line"""
        return platform.machine()

    def test_default_install(self):
        """Install LiteIDE from scratch test case"""

        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

        self.check_and_kill_process(["liteide", self.installed_path],
                                    wait_before=self.TIMEOUT_START, send_sigkill=True)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(r"LiteIDE is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()


class VSCodiumTests(LargeFrameworkTests):
    """Tests for VSCodium"""

    TIMEOUT_INSTALL_PROGRESS = 120
    TIMEOUT_START = 20
    TIMEOUT_STOP = 20

    def setUp(self):
        super().setUp()
        self.installed_path = os.path.join(self.install_base_path, "ide", "vscodium")
        self.desktop_filename = "vscodium.desktop"
        self.command_args = f'{UMAKE} ide vscodium'
        self.name = "VSCodium"

    def test_default_install(self):
        """Install VSCodium from scratch test case"""

        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"Choose installation path: {self.installed_path}")
        self.child.sendline("")
        self.expect_and_no_warn(r"Installation done", timeout=self.TIMEOUT_INSTALL_PROGRESS)
        self.wait_and_close()

        # we have an installed launcher, added to the launcher and an icon file
        self.assertTrue(self.launcher_exists_and_is_pinned(self.desktop_filename))
        self.assert_exec_exists()
        self.assert_icon_exists()
        self.assert_exec_link_exists()

        # launch it, send SIGTERM and check that it exits fine
        proc = subprocess.Popen(self.command_as_list(self.exec_path), stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)

        self.check_and_kill_process(["codium", self.installed_path],
                                    wait_before=self.TIMEOUT_START, send_sigkill=True)
        proc.communicate()
        proc.wait(self.TIMEOUT_STOP)

        # ensure that it's detected as installed:
        self.child = spawn_process(self.command(self.command_args))
        self.expect_and_no_warn(f"{self.name} is already installed.*\[.*\] ")
        self.child.sendline()
        self.wait_and_close()
