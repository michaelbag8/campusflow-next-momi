from campusflow.errors import (
    NotFoundError,
    StorageError,
    TransitionError,
    ValidationError,
)
from campusflow.notes import add_note, get_notes
from campusflow.reports import build_report, format_report
from campusflow.search import search_tickets, sort_by_priority_then_id
from campusflow.storage import FILENAME, load_tickets, save_tickets
from campusflow.tickets import create_ticket, list_tickets, view_ticket
from campusflow.understanding_check import QUESTION_BANK, run_check
from campusflow.workflow import (
    assign_ticket,
    change_status,
    get_work_queue,
    reopen_ticket,
)


def display_menu(output_func=print):
    menu_text = """
    ┌────────────────────────────────────────────────────────┐
    │                   CAMPUS WORKFLOW SYSTEM               │
    └────────────────────────────────────────────────────────┘

      [ Ticket Management ]
        1.  Create Ticket
        2.  List All Tickets
        3.  View Ticket Details
        4.  Assign Ticket to Staff
        5.  Change Ticket Status
        8.  Reopen Ticket

      [ Collaboration & Search ]
        10. Add Follow-Up Note
        11. View Ticket Notes
        12. Search Tickets
    

      [ Insights & Quality ]
        6.  Work Queue Overview
        7.  Standard Reports
        13. Engineering Understanding Check

      [ System ]
        9.  Exit
    ──────────────────────────────────────────────────────────
    """
    output_func(menu_text)



def _prompt_valid_choice(input_func, output_func, prompt, valid_values):
    while True:
        value = input_func(prompt).strip()
        if value == "":
            return ""
        if value.casefold() in {item.casefold() for item in valid_values}:
            return value
        output_func(f"Invalid value. Choose from: {', '.join(valid_values) or 'blank'}")


def main(input_func=input, output_func=print, storage_path=None):
    path = storage_path or FILENAME
    try:
        tickets = load_tickets(path)
    except StorageError as error:
        output_func(f"Could not load tickets: {error}")
        tickets = []

    while True:
        display_menu(output_func)
        choice = input_func("Select action: ").strip()

        try:
            if choice == "1":
                create_ticket(tickets)
                save_tickets(path, tickets)

            elif choice == "2":
                list_tickets(tickets, output_func=output_func)

            elif choice == "3":
                view_ticket(tickets, input_func=input_func, output_func=output_func)

            elif choice == "4":
                ticket_id = input_func("Ticket ID: ").strip().upper()
                staff_name = input_func("Staff name: ")
                assign_ticket(tickets, ticket_id, staff_name)
                save_tickets(path, tickets)
                output_func("Ticket assigned successfully.")

            elif choice == "5":
                ticket_id = input_func("Ticket ID: ").strip().upper()
                new_status = input_func("New status (open/in_progress/resolved): ")
                change_status(tickets, ticket_id, new_status)
                save_tickets(path, tickets)
                output_func("Ticket status updated successfully.")

            elif choice == "6":
                queue = get_work_queue(tickets)
                if not queue:
                    output_func("No unresolved tickets.")
                else:
                    for ticket in queue:
                        output_func(
                            f'{ticket["id"]} | {ticket["priority"]} | {ticket["title"]} | {ticket["status"]}'
                        )

            elif choice == "7":
                report = build_report(tickets)
                output_func(format_report(report))

            elif choice == "8":
                ticket_id = input_func("Ticket ID: ").strip().upper()
                reopen_ticket(tickets, ticket_id)
                save_tickets(path, tickets)
                output_func("Ticket reopened successfully.")

            elif choice == "9":
                output_func("Goodbye!")
                break

            elif choice == "10":
                ticket_id = input_func("Ticket ID: ").strip().upper()
                author = input_func("Author: ")
                message = input_func("Message: ")
                note = add_note(tickets, ticket_id, author, message)
                save_tickets(path, tickets)
                output_func(f"Note added: {note['note_id']}")

            elif choice == "11":
                ticket_id = input_func("Ticket ID: ").strip().upper()
                notes = get_notes(tickets, ticket_id)
                if not notes:
                    output_func("No notes for this ticket.")
                else:
                    for note in notes:
                        output_func(f"{note['note_id']} | {note['author']} | {note['message']}")

            elif choice == "12":
                title_query = input_func("Title contains (blank for any): ").strip()
                category = input_func("Category (blank for any): ").strip()
                while category and category.casefold() not in {"network", "hardware", "software", "other"}:
                    output_func("Invalid category. Use Network, Hardware, Software, Other or blank.")
                    category = input_func("Category (blank for any): ").strip()
                status = input_func("Status (blank for any): ").strip().casefold()
                while status and status not in {"open", "in_progress", "resolved"}:
                    output_func("Invalid status. Use open, in_progress, resolved or blank.")
                    status = input_func("Status (blank for any): ").strip().casefold()
                priority = input_func("Priority (blank for any): ").strip().casefold()
                while priority and priority not in {"critical", "high", "medium", "low"}:
                    output_func("Invalid priority. Use critical, high, medium, low or blank.")
                    priority = input_func("Priority (blank for any): ").strip().casefold()
                results = search_tickets(tickets, title_query, category, status, priority)
                if not results:
                    output_func("No tickets match the supplied filters.")
                else:
                    for ticket in results:
                        output_func(f"{ticket['id']} | {ticket['title']} | {ticket['status']} | {ticket['priority']}")

            elif choice == "15":
                title_query = input_func("Title contains (blank for any): ").strip()
                category = input_func("Category (blank for any): ").strip()
                while category and category.casefold() not in {"network", "hardware", "software", "other"}:
                    output_func("Invalid category. Use Network, Hardware, Software, Other or blank.")
                    category = input_func("Category (blank for any): ").strip()
                status = input_func("Status (blank for any): ").strip().casefold()
                while status and status not in {"open", "in_progress", "resolved"}:
                    output_func("Invalid status. Use open, in_progress, resolved or blank.")
                    status = input_func("Status (blank for any): ").strip().casefold()
                priority = input_func("Priority (blank for any): ").strip().casefold()
                while priority and priority not in {"critical", "high", "medium", "low"}:
                    output_func("Invalid priority. Use critical, high, medium, low or blank.")
                    priority = input_func("Priority (blank for any): ").strip().casefold()
                results = sort_by_priority_then_id(search_tickets(tickets, title_query, category, status, priority))
                if not results:
                    output_func("No tickets match the supplied filters.")
                else:
                    for ticket in results:
                        output_func(f"{ticket['id']} | {ticket['title']} | {ticket['status']} | {ticket['priority']}")

            elif choice == "14":
                report = build_report(tickets)
                output_func(format_report(report))

            elif choice == "13":
                run_check(QUESTION_BANK, input_func, output_func, "learning_notes.txt")

            else:
                output_func("Invalid choice. Select an option between 1 and 15.")

        except (ValidationError, TransitionError, NotFoundError, StorageError, ValueError, OSError) as error:
            output_func(f"Error: {error}")


if __name__ == "__main__":
    main()