""" doc """
import pytest


class TestClass1(object):
    """ doc """
    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc001")
    def test_0001(self):
        """
        @Title: IDM-IPA-TC: test suite: test case 0001
        """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc002")
    def test_0002(self):
        """
        @Title: IDM-IPA-TC: test suite: test case 0002
        """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc003")
    def test_0003(self):
        """
        @Title: IDM-IPA-TC: test suite: test case 0003
        """
        pass

    def test_0004(self):
        """ IDM-IPA-TC: test suite: test case 0004 """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc004")
    def test_0005(self):
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc006")
    def test_0006(self):
        """
        :Title: IDM-IPA-TC: test suite: test case 0006
        """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc007")
    def test_0007(self):
        """
        :title: IDM-IPA-TC: test suite: test case 0007
        """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc008")
    def test_0008(self):
        """
        :Title :      IDM-IPA-TC: test suite: test case 0008
        """
        pass

    @pytest.mark.xmlprop("my-test-id", "IDM-IPA-TC-test123-tc009")
    def test_0009(self):
        """
        :title   :    IDM-IPA-TC: test suite: test case 0009
        """
        pass

    def test_000010(self):
        """
        @Title: IDM-SSSD-TC: test provider: test_suite
        This is a long test case name example containing
        more than 80 characters 
        """
        pass

    def test_000011(self):
        """
        
        :title:  IDM-SSSD-TC: test suite: test case 000011
        This is a very very long test case name containing more than
        120 characters in the test case title
        """
        pass


    def test_000012(self):
        """
        :title:  IDM-SSSD-TC: test suite: test case 000012
         This is a very very very very long test case name containing more than
         120 characters in the test case title

        @Description: This is a test case description
        """

    def test_000013(self):
        """
        @Title: IDM-SSSD-TC: test provider: test_suite
        @Id: Testcase ID:0000
        """
        pass

    def test_000014(self):
        """
        :title   :    IDM-IPA-TC: test suite: test case 00014
        :description: Test case descrption
        """
        pass

    def test_000015(self):
        """
        @Title: IDM-SSSD-TC: test provider: test_suite
        This is a long test case name example containing
        more than 80 characters 
        @Description: This is a test case description
        """
        pass

    def test_000016(self):
        """
        :title: IDM-IPA-TC: Feature: verify abc user is able to login
        :id: test_case_00016
        """
        pass

    def test_000017(self):
        """
        :title: IDM-IPA-TC: Feature: verify abc user is able to login
        and all the groups user is member is shown in 
        id command
        :id: test_case_00017
        """
        pass

