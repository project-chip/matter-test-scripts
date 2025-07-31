#
# Copyright (c) 2023 Project CHIP Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from app.test_engine.logger import test_engine_logger as logger
from app.test_engine.models import TestStep

from ..onboarding_script_support import PayloadParsingTestBaseClass


class TCDD13(PayloadParsingTestBaseClass):
    metadata = {
        "public_id": "TC-DD-1.3",
        "version": "0.0.1",
        "title": "TC-DD-1.3",
        "description": """This test case verifies that
        the NFC tag's onboarding payload contains the
        necessary information to onboard the device
        onto the Matter network.""",
    }

    @classmethod
    def pics(cls) -> set[str]:
        return set(
            [
                "MCORE.ROLE.COMMISSIONEE",
                "MCORE.DD.NFC",
            ]
        )

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep(
                "Step1: Power up the DUT and put the DUT in pairing mode\
                     and bring the NFC code reader close to the DUT"
            ),

            TestStep("""Step3.a: Verify the NFC's onboarding payload code version\
                     - Verify the NFC's onboarding payload code version is '000'"""),

            TestStep("""Step3.b: Verify 8-bit Discovery Capabilities bit mask\
                Verify that the onboarding payload contains an 8-bit Discovery Capabilities bitmask. Each bit must represent the following transport support:

                - Bit 0 - Reserved (SHALL be 0)\
                - Bit 1 - BLE: - 0: Device does not support BLE for discovery or is currently commissioned into one or more fabrics. - 1: Device supports BLE for discovery when not commissioned.\
                - Bit 2 - On IP network: - 1: Device is already on the IP network\
                - Bits 3 - Wi-Fi Public Action Frame: - 0: Device does not support Wi-Fi Public Action Frame for discovery or is currently commissioned into one or more fabrics. - 1: Device supports Wi-Fi Public Action Frame for discovery when not commissioned.\
                - Bits 7-4 - Reserved (SHALL be 0)\
                - Ensure that the bitmask accurately reflects the DUT’s supported commissioning methods and no reserved bits are set."""),

            TestStep("""Step3.c: Verify the 12-bit discriminator bit mask\
                     - Verify the 12-bit discriminator matches the value which a device advertises during commissioning."""),

            TestStep("""Step3.d: Verify the onboarding payload contains a 27-bit Passcode\
                     - Verify the 27-bit unsigned integer encodes an 8-digit decimal numeric value and shall be a value between 0x0000001 to 0x5f5e0fe (00000001 to 99999998)"""),

            TestStep("""Step3.f: Verify NFC's onboarding payload code prefix\
                     - Verify NFC's onboarding payload code prefix is "MT:"""),

            TestStep("""Step3.g: Verify Vendor ID and Product ID\
                     - Verify Vendor ID and Product ID match the values submitted by manufacturer in Distributed Compliance Ledger"""),

            TestStep("""Step5: Verify Custom payload support\
                     - Verify the custom payload is a 2 bit field and the Values supported are 0, 1 and 2."""),
        ]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        # Test step 1: Power up the DUT and put the DUT in pairing mode

        # Test step 2: Bring the NFC code reader close to the DUT"

        # Prompt user for the NFC code payload from UI/NFC code reader.
        prompt_request = self.create_onboarding_code_payload_prompt("NFC")
        prompt_response = await self.invoke_prompt_and_get_str_response(prompt_request)
        logger.info(f"User input : {prompt_response}")

        # Parsing the NFC oboarding code payload response
        nfc_code_payload = await self.chip_tool_parse_onboarding_code(prompt_response)
        logger.info(f"Parsed payload : {nfc_code_payload}")

        # Test step 3.a
        self.next_step()
        logger.info("Verifying the NFC's onboarding payload code version...")
        self.payload_version_check(nfc_code_payload.version)

        # Test step 3.b
        self.next_step()
        logger.info("Verifying the 8-bit Discovery Capabilities bit mask...")
        self.payload_rendezvous_capabilities_bit_mask_check(
            nfc_code_payload.rendezvousInfo
        )

        # Test step 3.c
        self.next_step()
        logger.info("Verifying the 12-bit discriminator bit mask...")
        # TODO Extract discriminator from device advertises frame Issue#186
        await self.payload_discriminator_check(nfc_code_payload.discriminator)

        # Test step 3.d
        self.next_step()
        logger.info("Verifying the onboarding payload contains a 27-bit passcode...")
        self.payload_passcode_check(nfc_code_payload.setUpPINCode)

        # Test step 3.f
        self.next_step()
        logger.info("Verifying NFC's onboarding payload code prefix...")
        nfc_code_prefix = prompt_response[:3]
        self.payload_prefix_check(nfc_code_prefix)

        # Test step 3.g
        self.next_step()
        logger.info("Verifying Vendor ID and Product ID...")
        self.vendorid_productid_check(
            nfc_code_payload.vendorID, nfc_code_payload.productID
        )

        # Test step 5
        self.next_step()
        logger.info("Verifying custom payload support...")
        self.custom_payload_support_check(nfc_code_payload.commissioningFlow)

    async def cleanup(self) -> None:
        logger.info("TC-DD-1.3 Cleanup")
