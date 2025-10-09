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


class TCDD11(PayloadParsingTestBaseClass):
    metadata = {
        "public_id": "TC-DD-1.1",
        "version": "0.0.1",
        "title": "TC-DD-1.1",
        "description": """This test case verifies
         that the onboarding QR code contains the
         necessary information to onboard the
         device onto the Matter network.""",
    }

    @classmethod
    def pics(cls) -> set[str]:
        return set(
            [
                "MCORE.ROLE.COMMISSIONEE",
                "MCORE.DD.QR",
            ]
        )

    def create_test_steps(self) -> None:
        self.test_steps = [
            TestStep("""Step1: Scan the DUT's QR code using a QR code reader
                     - Verify the QR code is scanned successfully."""),

            TestStep("""Step2.a: Verify the QR code payload version
                     - Verify the QR code payload version is '000'."""),

            TestStep("""Step2.b: Verify Vendor ID and Product ID
                     - Verify Vendor ID and Product ID match the values submitted by manufacturer in Distributed Compliance Ledger"""),

            TestStep("""Step2.c: Verify the Custom Flow bit
                     - Verify the Custom Flow bit has one of the following values: 0, 1 or 2"""),

            TestStep(""""Step2.d: Verify 8-bit Discovery Capabilities bit mask
                     Verify that the onboarding payload contains an 8-bit Discovery Capabilities bitmask. Each bit must represent the following transport support:

                     - Bit 0 - Reserved (SHALL be 0)
                     - Bit 1 - BLE: - 0: Device does not support BLE for discovery or is currently commissioned into one or more fabrics. - 1: Device supports BLE for discovery when not commissioned.
                     - Bit 2 - On IP network: - 1: Device is already on the IP network
                     - Bits 3 - Wi-Fi Public Action Frame: - 0: Device does not support Wi-Fi Public Action Frame for discovery or is currently commissioned into one or more fabrics. - 1: Device supports Wi-Fi Public Action Frame for discovery when not commissioned.
                     - Bits 7-4 - Reserved (SHALL be 0)
                     - Ensure that the bitmask accurately reflects the DUT's supported commissioning methods and no reserved bits are set."""),

            TestStep("""Step2.e: Verify the 12-bit discriminator bit mask
                     - Verify the 12-bit discriminator matches the value which a device advertises during commissioning."""),

            TestStep("""Step2.f: Verify the onboarding payload contains a 27-bit Passcode
                     - Verify the 27-bit unsigned integer encodes an 8-digit decimal numeric value and shall be a value between 0x0000001 to 0x5f5e0fe (00000001 to 99999998)"""),

            TestStep("""Step2.g: Verify passcode is valid
                     - Verify passcode does not use any trivial values: 00000000, 11111111, 22222222, 33333333, 44444444, 55555555, 66666666, 77777777, 88888888, 99999999, 12345678, 87654321
                     - Verify Passcode is not derived from public information as serial number, manufacturer date, MAC address, region of origin etc."""),

            TestStep("""Step2.h: Verify QR code prefix
                     - Verify QR code prefix is "MT:"""),

            TestStep("""Step3: Verify the packed binary data structure
                     - Verify the packed binary data structure is padded with '0' bits at the end of the structure to the nearest byte boundary."""),
        ]

    async def setup(self) -> None:
        logger.info("This is a test case setup")

    async def execute(self) -> None:
        # Test step 1
        # Fetch QR code payload from UI/QR code reader.
        prompt_request = self.create_onboarding_code_payload_prompt("QR")
        prompt_response = await self.invoke_prompt_and_get_str_response(prompt_request)
        logger.info(f"User input : {prompt_response}")

        # Parse the onboarding QR code payload response
        qr_code_payload = await self.chip_tool_parse_onboarding_code(prompt_response)
        logger.info(f"parsed payload : {qr_code_payload}")

        # Test step 2.a
        # Verify the QR code payload version
        self.next_step()
        logger.info("Verifying the QR code payload version...")
        self.payload_version_check(qr_code_payload.version)

        # Test step 2.b
        # Verify Vendor ID and Product ID
        self.next_step()
        logger.info("Verifying Vendor ID and Product ID...")
        self.vendorid_productid_check(
            qr_code_payload.vendorID, qr_code_payload.productID
        )

        # Test step 2.c
        # Verify the Custom Flow bit
        logger.info("Verifying the Custom Flow bit...")
        self.next_step()
        self.custom_payload_support_check(qr_code_payload.commissioningFlow)

        # Test step 2.d
        # Verify 8-bit Discovery Capabilities bit mask
        self.next_step()
        logger.info("Verifying 8-bit Discovery Capabilities bit mask...")
        self.payload_rendezvous_capabilities_bit_mask_check(
            qr_code_payload.rendezvousInfo
        )

        # Test step 2.e
        # Verify the 12-bit discriminator bit mask
        self.next_step()
        logger.info("Verifying the 12-bit discriminator bit mask...")
        await self.payload_discriminator_check(qr_code_payload.discriminator)
        # TODO Extract discriminator from device advertises frame Issue#186

        # Test steps 2.f, 2.g
        # Verify the onboarding payload contains a 27-bit Passcode
        # Verify passcode is valid
        self.next_step()
        self.next_step()
        logger.info("Verifying the onboarding payload contains a 27-bit Passcode and is valid...")
        self.payload_passcode_check(qr_code_payload.setUpPINCode)

        # Test step 2.h
        # Verify QR code prefix
        self.next_step()
        logger.info("Verifying QR code prefix...")
        qr_code_prefix = prompt_response[:3]
        self.payload_prefix_check(qr_code_prefix)

        # Test step 3
        # Verify the packed binary data structure
        self.next_step()
        logger.info("Verifying the packed binary data structure...")
        # TODO: Step exists in test plan but is not implemented


    async def cleanup(self) -> None:
        logger.info("TC-DD-1.1 Cleanup")
