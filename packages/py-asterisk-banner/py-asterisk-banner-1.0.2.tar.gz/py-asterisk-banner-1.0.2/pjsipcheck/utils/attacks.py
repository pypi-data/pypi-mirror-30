class Attacks:

    @staticmethod
    def is_sip(line):
        if "rejected" in line:
            return True
        elif "Wrong password" in line:
            return True
        elif "failed to authenticate" in line:
            return True

        return False

    @staticmethod
    def is_pjsip(line):
        if "No matching endpoint found" in line:
            return True

        return False
