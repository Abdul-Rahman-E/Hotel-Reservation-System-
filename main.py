import random
import datetime
import jinja2
import pdfkit


class Hotel:
    def __init__(self, hotel_name, hotel_location):
        """
                Initialize a Hotel object.

                Parameters:
                - hotel_name (str): The name of the hotel.
                - hotel_location (str): The location of the hotel.

        """
        self._hotel_name = hotel_name
        self._hotel_location = hotel_location

    def get_hotel_name(self):
        """
                Get the name of the hotel.

                Returns:
                - str: The name of the hotel.

        """
        return self._hotel_name

    def get_hotel_location(self):
        """
                Get the location of the hotel.

                Returns:
                - str: The location of the hotel.

        """
        return self._hotel_location


class Rooms:
    def __init__(self, room_type, num_of_room, room_price):
        """
                Initialize a Rooms object.

                Parameters:
                - room_type (str): The type of room.
                - num_of_room (int): The number of rooms available.
                - room_price (int): The price per night for the room.

        """
        self._room_type = room_type
        self._num_of_room = num_of_room
        self._room_price = room_price
        self._list_of_rooms = {f'{self._room_type[0]}{x}': 'empty' for x in range(1, self._num_of_room + 1)}

    def get_room_type(self):
        """
                Get the type of room.

                Returns:
                - str: The type of room.

        """
        return self._room_type

    def room_available(self):
        """
                Get a list of available rooms.

                Returns:
                - list: A list of available room numbers.

        """
        return [x for x, y in self._list_of_rooms.items() if y == 'empty']

    def room_status(self):
        """
                Get the status of all rooms.

                Returns:
                - dict: A dictionary with room numbers as keys and their status as values.

        """
        return self._list_of_rooms

    def get_room_price(self):
        """
                Get the price per night for the room.

                Returns:
                - int: The price per night for the room.

        """
        return self._room_price

    def set_room_price(self, new_r_price):
        """
                Set a new price per night for the room.

                Parameters:
                - new_r_price (int): The new price per night for the room.

        """
        self._room_price = new_r_price

    def change_status(self, room_no, status):
        """
                Change the status of a room.

                Parameters:
                - room_no (str): The room number.
                - status (str): The new status of the room.

        """
        self._list_of_rooms[room_no] = status


class System:
    def __init__(self, wallet_class_name):
        """
                Initialize a System object.

                Parameters:
                - wallet_class_name (class): The class for the wallet object.

        """
        self.wallet = wallet_class_name(0)
        self.ADVANCE_PAYMENT_PERCENTAGE = 25 // 100

    def book(self, room_number, room_type_object, customer_object, hotel_object, calendar_object):
        """
                Book a room for a customer.

                Parameters:
                - room_number (str): The room number.
                - room_type_object (Rooms): The object representing the type of room.
                - customer_object (Customer): The object representing the customer.
                - hotel_object (Hotel): The object representing the hotel.
                - calendar_object (Calendar): The object representing the calendar.

        """
        if room_number in room_type_object.room_available():
            if not customer_object.advance_payment:
                customer_object.advance_payment = True
                self.wallet.add_to_wallet((room_type_object.get_room_price()) * self.ADVANCE_PAYMENT_PERCENTAGE)
                customer_object.set_price_of_booking((room_type_object.get_room_price()) * self.ADVANCE_PAYMENT_PERCENTAGE)
                customer_object.set_remaining_amount(room_type_object.get_room_price() -
                                                     customer_object.get_customer_details()['pob'])
                room_type_object.change_status(room_number, 'booked')
                customer_object.set_room(room_number)
                customer_object.set_room_type(room_type_object.get_room_type())
                customer_object.set_hotel_name(hotel_object.get_hotel_name)
                customer_object.set_hotel_location(hotel_object.get_hotel_location)
                customer_object.set_booking_date(calendar_object.get_current_date())
                customer_object.set_booking_time(calendar_object.get_current_time())
                print(f"Your booking for the room {room_number} is confirmed!")

        else:
            if room_number[0] != room_type_object.room_available()[0][0]:
                print("There is no room available with this number!")
            print(f'The room number {room_number} is already occupied!')

    def cancel(self, room_number, room_type_object, customer_object):
        """
                Cancel a customer's booking.

                Parameters:
                - room_number (str): The room number.
                - room_type_object (Rooms): The object representing the type of room.
                - customer_object (Customer): The object representing the customer.

        """
        if customer_object.get_customer_details()['room_no'] == room_number and \
                room_type_object.room_status()[room_number] == "booked":
            self.wallet.send_from_wallet(customer_object.get_customer_details()['pob'] * 0.82)
            room_type_object.room_status()[room_number] = "empty"
            customer_object.delete_customer()

    @staticmethod
    def check_in_mark(customer_object, date, time):
        """
                Mark the check-in date and time for a customer.

                Parameters:
                - customer_object (Customer): The object representing the customer.
                - date (str): The check-in date.
                - time (str): The check-in time.

        """
        customer_object.set_check_in_date(date)
        customer_object.set_check_in_time(time)

    @staticmethod
    def check_out_mark(customer_object, room_object, date, time):
        """
                Mark the check-out date and time for a customer and change room status to empty.

                Parameters:
                - customer_object (Customer): The object representing the customer.
                - room_object (Rooms): The object representing the room.
                - date (str): The check-out date.
                - time (str): The check-out time.

        """
        customer_object.set_check_out_date(date)
        customer_object.set_check_out_time(time)
        room_object.change_status(customer_object.get_customer_details()['room_no'], 'empty')

    def final_payment(self, customer_object, room_object, bill_class):
        """
                Process the final payment for a customer, generate a bill, and delete the customer.

                Parameters:
                - customer_object (Customer): The object representing the customer.
                - room_object (Rooms): The object representing the room.
                - bill_class (Bill): The object representing the bill.

        """
        customer_object.payment_is_done = True
        self.wallet.add_to_wallet(customer_object.get_customer_details()['remaining_amount'])
        room_object.change_status(customer_object.get_customer_details()['room_no'], 'empty')
        difference = int(customer_object.get_customer_details()['check_out_date'][0:2]) - int(
            customer_object.get_customer_details()['check_in_date'][0:2])
        customer_object.set_number_of_nights(difference)
        bill_class.generate_bill(customer_object, bill_class)
        customer_object.delete_customer()


class Customer:
    def __init__(self, customer_name, phone_number, email):
        """
                Initialize a Customer object.

                Parameters:
                - customer_name (str): The name of the customer.
                - phone_number (int): The phone number of the customer.
                - email (str): The email address of the customer.

        """
        self._customer_details = {
            'customer_name': customer_name,
            'phone_number': phone_number,
            'customer_id': self.set_customer_id(),
            'email': email,
        }
        self.advance_payment = False
        self.payment_is_done = False

    def get_customer_details(self):
        """
                Get the details of the customer.

                Returns:
                - dict: A dictionary containing customer details.

        """
        return self._customer_details

    def get_customer_name(self):
        """
                Get the name of the customer.

                Returns:
                - str: The name of the customer.

        """
        return self._customer_details['customer_name']

    def get_phone_number(self):
        """
                Get the phone number of the customer.

                Returns:
                - int: The phone number of the customer.

        """
        return self._customer_details['phone_number']

    def set_room(self, room_no):
        """
                Set the room number for the customer.

                Parameters:
                - room_no (str): The room number.

        """
        self._customer_details['room_no'] = room_no

    def set_room_type(self, room_type):
        """
                Set the room type for the customer.

                Parameters:
                - room_type (str): The room type.

        """
        self._customer_details['room_type'] = room_type

    def set_booking_time(self, booking_time):
        """
                Set the booking time for the customer.

                Parameters:
                - booking_time (str): The booking time.

        """
        self._customer_details['booking_time'] = booking_time

    def set_booking_date(self, booking_date):
        """
                Set the booking date for the customer.

                Parameters:
                - booking_date (str): The booking date.

        """
        self._customer_details['booking_date'] = booking_date

    def set_check_in_date(self, check_in_date):
        """
                Set the check-in date for the customer.

                Parameters:
                - check_in_date (str): The check-in date.

        """
        self._customer_details['check_in_date'] = check_in_date

    def set_check_in_time(self, check_in_time):
        """
                Set the check-in time for the customer.

                Parameters:
                - check_in_time (str): The check-in time.

        """
        self._customer_details['check_in_time'] = check_in_time

    def set_check_out_date(self, check_out_date):
        """
                Set the check-out date for the customer.

                Parameters:
                - check_out_date (str): The check-out date.

        """
        self._customer_details['check_out_date'] = check_out_date

    def set_check_out_time(self, check_out_time):
        """
                Set the check-out time for the customer.

                Parameters:
                - check_out_time (str): The check-out time.

        """
        self._customer_details['check_out_time'] = check_out_time

    def set_price_of_booking(self, pob):
        """
                Set the price of booking for the customer.

                Parameters:
                - pob (int): The price of booking.

        """
        self._customer_details['pob'] = pob

    def set_remaining_amount(self, remaining_amount):
        """
                Set the remaining amount for the customer.

                Parameters:
                - remaining_amount (int): The remaining amount to be paid.

        """
        self._customer_details['remaining_amount'] = remaining_amount

    def set_number_of_nights(self, no_of_night):
        """
                Set the number of nights the customer stayed.

                Parameters:
                - no_of_night (int): The number of nights.

        """
        self._customer_details['no_of_nights'] = no_of_night

    def set_hotel_name(self, hotel_name):
        """
                Set the hotel name for the customer.

                Parameters:
                - hotel_name (str): The hotel name.

        """
        self._customer_details['hotel_name'] = hotel_name()

    def set_hotel_location(self, hotel_location):
        """
                Set the hotel location for the customer.

                Parameters:
                - hotel_location (str): The hotel location.

        """
        self._customer_details['hotel_location'] = hotel_location()

    def delete_customer(self):
        """
                Delete the customer's details.

                This method removes the customer's details, resets payment flags, and clears the customer's data.

        """
        self._customer_details = {}
        self.payment_is_done = False
        self.advance_payment = False

    @staticmethod
    def set_customer_id():
        """
            Generate a unique customer ID.

            :return: Unique customer ID.

        """
        letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        numbers = '0123456789'
        bill_id = [random.choice(letters) for _ in range(3)] + [random.choice(numbers) for _ in range(7)]
        random.shuffle(bill_id)
        return '#' + ''.join(bill_id)


class Calendar:
    """
        Class representing a calendar for managing dates and times.
    """
    @staticmethod
    def get_current_time():
        """
                Get the current time.

                :return: Current time.
        """
        return datetime.datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def get_current_date():
        """
                Get the current date.

                :return: Current date.

        """
        return datetime.datetime.now().strftime("%d-%m-%Y")


class Bill:
    """
        A class representing the billing system.

        Attributes:
            bill_number (int): A class variable to track the bill number.

        Methods:
            get_bill_number(): A static method to get the next bill number.
            generate_bill(customer_object, bill_class): A static method to generate a bill.

    """
    bill_number = 0

    @staticmethod
    def get_bill_number():
        """Increment and return the bill number."""
        Bill.bill_number += 1
        return Bill.bill_number

    @staticmethod
    def generate_bill(customer_object, bill_class):
        """
                Generate a bill using customer details and save it as a PDF.

                Args:
                    customer_object (Customer): An instance of the Customer class.
                    bill_class (Bill): An instance of the Bill class.

        """
        hotel_name = customer_object.get_customer_details()['hotel_name']
        location = customer_object.get_customer_details()['hotel_location']
        guest_name = customer_object.get_customer_details()['customer_name']
        guest_email = customer_object.get_customer_details()['email']
        guest_phone = customer_object.get_customer_details()['phone_number']
        booking_id = customer_object.get_customer_details()['customer_id']
        check_in_date = customer_object.get_customer_details()['check_in_date']
        check_out_date = customer_object.get_customer_details()['check_out_date']
        room_type = customer_object.get_customer_details()['room_type']
        room_number = customer_object.get_customer_details()['room_no']
        price_per_night = customer_object.get_customer_details()['pob']
        number_of_nights = customer_object.get_customer_details()['no_of_nights']
        subtotal = number_of_nights * price_per_night
        tax = (18 / 100) * subtotal
        total = subtotal + tax
        context = {'hotel_name': hotel_name,
                   'location': location.capitalize(),
                   'guest_name': guest_name,
                   'guest_email': guest_email,
                   'guest_phone': guest_phone,
                   'booking_id': booking_id,
                   'check_in_date': check_in_date,
                   'check_out_date': check_out_date,
                   'room_type': room_type,
                   'room_number': room_number,
                   'price_per_night': price_per_night,
                   'number_of_nights': number_of_nights,
                   'subtotal': subtotal,
                   'tax': tax,
                   'total': total, }

        template_loader = jinja2.FileSystemLoader('./')
        template_env = jinja2.Environment(loader=template_loader)

        template = template_env.get_template("bill_template.html")
        output_text = template.render(context)

        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
        pdfkit.from_string(output_text, f'{bill_class.get_bill_number()}.pdf', configuration=config)


class Wallet:
    def __init__(self, balance):
        """
            A class representing a customer's wallet.

            Attributes:
                balance (float): The balance in the wallet.

            Methods:
                add_to_wallet(amount): Add an amount to the wallet balance.
                send_from_wallet(amount): Subtract an amount from the wallet balance.
            """
        self._balance = balance

    def add_to_wallet(self, amount):
        """Initialize the wallet with a given balance."""
        self._balance += amount

    def send_from_wallet(self, amount):
        """Subtract an amount from the wallet balance."""
        self._balance -= amount


taj = {
    'hotel': Hotel('The Taj Residency', 'united kingdom'),
    'room': {
        'standard': Rooms('standard', 15, 28000),
        'deluxe': Rooms('deluxe', 8, 55000),
        'executive': Rooms('executive', 5, 112000)
    }
}

buck = {
    'hotel': Hotel('The Buckingham Palace', 'england'),
    'room': {
        'standard': Rooms('standard', 20, 35000),
        'deluxe': Rooms('deluxe', 8, 85000),
        'executive': Rooms('executive', 5, 322000)
    }
}

hotel_reservation_system = System(Wallet)

john = Customer('john smith', 8654129821, 'johnsmithcole@hotmail.com')
kyle = Customer('kyle pecker', 8221533110, 'kyle12peck@outlook.com')

print('The total available deluxe rooms: ' + ', '.join(taj['room']['deluxe'].room_available()))

hotel_reservation_system.book('d2', taj['room']['deluxe'], john, taj['hotel'], Calendar)

print('The total available executive rooms: ' + ', '.join(buck['room']['executive'].room_available()))
hotel_reservation_system.book('e3', buck['room']['executive'], kyle, buck['hotel'], Calendar)

hotel_reservation_system.check_in_mark(john, '11-01-2024', '13:25:44')
hotel_reservation_system.check_in_mark(kyle, Calendar.get_current_date(), Calendar.get_current_time())

hotel_reservation_system.check_out_mark(john, taj['room']['deluxe'], Calendar.get_current_date(), '19:27:12')
hotel_reservation_system.check_out_mark(kyle, buck['room']['executive'], '18-01-2024', '22:12:55')

hotel_reservation_system.final_payment(john, taj['room']['deluxe'], Bill)
hotel_reservation_system.final_payment(kyle, buck['room']['deluxe'], Bill)
