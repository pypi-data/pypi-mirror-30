import unittest
import pyzipcode


class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.db = pyzipcode.ZipCodeDatabase()

    def test_retrieves_zip_code_information(self):
        zip = self.db['54115']
        self.assertEqual(zip.zip, '54115')
        self.assertEqual(zip.place, "De Pere")
        self.assertEqual(zip.state, "WI")
        
    def test_correct_latitude_value(self):
        zip = self.db[54115]
        self.assertTrue(44.43 < zip.latitude < 44.44)
    
    def test_correct_longitude_value(self):
        zip = self.db[54115]
        self.assertTrue(-88.09 < zip.longitude < -88.08)

    def test_radius(self):
        zips = self.db.get_zipcodes_around_radius('54115', 30)
        self.assertTrue('54304' in [zip.zip for zip in zips])
        
    def test_find_zip_by_place(self):
        zip = self.db.find_zip(place="De Pere")[0]
        self.assertEqual('54115', zip.zip)
        
    def test_find_zip_by_place_with_multiple_zips(self):
        zips = self.db.find_zip(place="Green Bay")
        self.assertTrue('54302' in [zip.zip for zip in zips])
        
    def test_find_zips_in_state(self):
        zips = self.db.find_zip(state="WI")
        self.assertTrue('54304' in [zip.zip for zip in zips])
        self.assertTrue('54901' in [zip.zip for zip in zips])

if __name__ == '__main__':
    unittest.main()
