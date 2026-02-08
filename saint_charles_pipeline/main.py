def main():
    # 1. Start session
    session = create_session()

    # 2. Submit search (7-day window)
    search_results = submit_search(session)

    # 3. Parse case list
    cases = parse_case_list(search_results)

    # 4. Filter valid probate cases
    valid_cases = filter_cases(cases)

    # 5. Loop cases
    for case in valid_cases:
        # 6. Visit case detail
        case_html = load_case_detail(session, case)

        # 7. Extract parties
        parties = extract_parties(case_html)

        # 8. Expand docket
        pdf_links = extract_docket_pdfs(case_html)

        # 9. Download PDFs
        for pdf in pdf_links:
            pdf_path = download_pdf(session, pdf)

            # 10. Parse PDFs
            phone = extract_phone_from_pdf(pdf_path)

            # 11. Stop if phone found
            if phone:
                break

        # 12. Save results
        save_result(case, phone)

