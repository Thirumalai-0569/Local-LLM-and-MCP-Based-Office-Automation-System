import streamlit as st
import pandas as pd
from pathlib import Path

from modules.ai_chat import ask_local_llm
from modules.vision_ai import analyze_image, check_vision_model
from modules.office_assistant import (
    read_excel_file, update_excel_cell, summarize_excel_file,
    create_word_file, read_word_file
)
from modules.dynamic_dashboard import render_dashboard
from modules.mcp_client import list_mcp_tools
from modules.office_assistant import (
    list_excel_sheets,
    update_excel_cell
)
st.set_page_config(page_title="Local-LLM-and-MCP-Based-Office-Automation-System", page_icon="", layout="wide")
st.title("Local-LLM-and-MCP-Based-Office-Automation-System")
st.caption("Local AI + Excel + Word + Screenshot Vision + Dynamic Dashboard + MCP")

for folder in ["uploads", "output/excel", "output/word"]:
    Path(folder).mkdir(parents=True, exist_ok=True)

tabs = st.tabs([" AI Chat", " Excel Assistant", " Word Assistant",
                " Screenshot AI", " Dynamic Dashboard", " MCP Tools"])

with tabs[0]:
    st.subheader("Chat with your local AI")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
    prompt = st.chat_input("Ask a question...")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking with Ollama..."):
                answer = ask_local_llm(st.session_state.chat_history)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

with tabs[1]:
    st.subheader("Excel Assistant")

    # Upload Excel workbook
    excel_file = st.file_uploader(
        "Upload Excel Sheet",
        type=["xlsx"],
        key="excel_assistant"
    )

    if excel_file is not None:

        try:
            # Get all existing worksheet names
            sheet_names = list_excel_sheets(excel_file)

            if not sheet_names:
                st.error("No worksheets found.")
            else:
                st.success(f"Uploaded: {excel_file.name}")

                # Select existing worksheet
                sheet_name = st.selectbox(
                    "Select Worksheet",
                    sheet_names,
                    key="main_excel_sheet"
                )

                # Display worksheet preview
                df = read_excel_file(
                    excel_file,
                    sheet_name
                )

                st.markdown("### Excel Preview")
                st.dataframe(df, use_container_width=True)

                st.divider()

                # Select Excel operation
                st.markdown("### Select Excel operation")

                operation = st.radio(
                    "Choose an operation",
                    [
                        "Summary of Excel",
                        "Update Excel Cell",
                        "Download Excel Sheet"
                    ],
                    horizontal=True,
                    key="excel_operation"
                )

                st.divider()

                # ------------------------------------------------
                # 1. EXCEL SUMMARY
                # ------------------------------------------------
                if operation == "Summary of Excel":

                    st.subheader("Excel Summary")

                    col1, col2, col3 = st.columns(3)

                    col1.metric("Total Rows", len(df))
                    col2.metric("Total Columns", len(df.columns))
                    col3.metric(
                        "Duplicate Rows",
                        int(df.duplicated().sum())
                    )

                    st.markdown("#### Missing Values")
                    st.dataframe(
                        df.isnull().sum().reset_index().rename(
                            columns={
                                "index": "Column",
                                0: "Missing Values"
                            }
                        ),
                        use_container_width=True
                    )

                    st.markdown("#### Statistical Summary")
                    st.dataframe(
                        df.describe(include="all").transpose(),
                        use_container_width=True
                    )

                    if st.button("Generate Detailed Summary"):
                        summary = summarize_excel_file(
                            excel_file,
                            sheet_name
                        )

                        st.text_area(
                            "Detailed Excel Summary",
                            summary,
                            height=300
                        )

                # ------------------------------------------------
                # 2. UPDATE EXCEL CELL
                # ------------------------------------------------
                elif operation == "Update Excel Cell":

                    st.subheader("Update Excel Cell")

                    # Three required fields
                    update_sheet = st.selectbox(
                        "Sheet name",
                        sheet_names,
                        key="update_sheet"
                    )

                    cell_address = st.text_input(
                        "Cell address",
                        placeholder="Example: A1, B5, G10",
                        key="update_address"
                    )

                    new_value = st.text_input(
                        "New cell value",
                        placeholder="Example: =SUM(B2:B10)",
                        key="update_value"
                    )

                    if st.button(
                        "Update Excel Cell",
                        type="primary"
                    ):

                        if not cell_address.strip():
                            st.warning("Enter a cell address.")

                        elif not new_value.strip():
                            st.warning("Enter a new cell value.")

                        else:
                            try:
                                excel_file.seek(0)

                                output_path = update_excel_cell(
                                    excel_file,
                                    update_sheet,
                                    cell_address,
                                    new_value
                                )

                                with open(output_path, "rb") as f:
                                    updated_data = f.read()

                                st.success(
                                    f"Updated {update_sheet}!{cell_address.upper()}"
                                )

                                st.download_button(
                                    "Download Updated Workbook",
                                    data=updated_data,
                                    file_name="updated_excel.xlsx",
                                    mime=(
                                        "application/vnd.openxmlformats-officedocument."
                                        "spreadsheetml.sheet"
                                    )
                                )

                            except Exception as e:
                                st.error(f"Update failed: {e}")

                # ------------------------------------------------
                # 3. DOWNLOAD EXCEL SHEET
                # ------------------------------------------------
                elif operation == "Download Excel Sheet":

                    st.subheader("Download Excel Sheet")

                    download_format = st.radio(
                        "Select download format",
                        ["Excel Workbook (.xlsx)", "CSV (.csv)"],
                        horizontal=True
                    )

                    if download_format == "CSV (.csv)":

                        csv_data = df.to_csv(index=False).encode("utf-8")

                        st.download_button(
                            "Download Selected Sheet as CSV",
                            data=csv_data,
                            file_name=f"{sheet_name}.csv",
                            mime="text/csv"
                        )

                    else:

                        excel_file.seek(0)
                        workbook_data = excel_file.getvalue()

                        st.download_button(
                            "Download Complete Excel Workbook",
                            data=workbook_data,
                            file_name=excel_file.name,
                            mime=(
                                "application/vnd.openxmlformats-officedocument."
                                "spreadsheetml.sheet"
                            )
                        )

        except Exception as e:
            st.error(f"Excel Assistant Error: {e}")


with tabs[2]:
    st.subheader("Word Assistant")
    word_file = st.file_uploader("Upload Word document", type=["docx"], key="word_upload")
    if word_file and st.button("Read Word document"):
        try:
            st.text_area("Document text", read_word_file(word_file), height=250)
        except Exception as e:
            st.error(str(e))
    st.markdown("#### Create a Word document")
    doc_title = st.text_input("Document title", "Office Meeting Notes")
    doc_body = st.text_area("Document content", "Meeting summary:\n\n1. Project updates\n2. Next steps")
    if st.button("Create Word document"):
        output_path = create_word_file(doc_title, doc_body)
        with open(output_path, "rb") as f:
            st.download_button("Download Word document", f.read(),
                               Path(output_path).name,
                               "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

with tabs[3]:
    st.subheader("Screenshot Vision AI")
    ready, status = check_vision_model()
    st.caption(status)
    image_file = st.file_uploader("Upload screenshot", type=["png", "jpg", "jpeg", "webp"], key="vision_upload")
    if image_file:
        st.image(image_file, caption="Uploaded screenshot", use_container_width=True)
        question = st.text_area("What should the AI inspect?",
                                "Describe this screenshot. Read visible text and identify any errors.")
        if st.button("Analyze screenshot"):
            with st.spinner("Ollama vision model is analyzing the image..."):
                result = analyze_image(image_file, question)
            st.markdown("#### Analysis")
            st.write(result)

with tabs[4]:
    st.subheader("Dynamic Excel Dashboard")
    dashboard_file = st.file_uploader("Upload Excel file for dashboard", type=["xlsx"], key="dashboard_upload")
    if dashboard_file:
        render_dashboard(dashboard_file)

with tabs[5]:
    st.subheader("MCP server connection test")
    st.write("This project includes a local MCP stdio server exposing Excel and Word tools.")
    if st.button("List MCP tools"):
        with st.spinner("Starting local MCP server..."):
            try:
                tools = list_mcp_tools()
                if tools:
                    for tool in tools:
                        st.markdown(f"**{tool['name']}** — {tool.get('description', '')}")
                else:
                    st.warning("No tools were returned. Check MCP installation.")
            except Exception as e:
                st.error(f"MCP connection failed: {type(e).__name__}: {e}")

st.divider()
st.caption("Local processing note: files are processed by this application on your computer. Ollama must be running for AI features.")


