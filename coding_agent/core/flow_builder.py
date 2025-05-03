from coding_agent.core.flow_foundation import Flow
from coding_agent.logger import setup_logger
from coding_agent.nodes.decision_nodes import MainDecisionAgent
from coding_agent.nodes.edit_nodes import ReadTargetFileNode, \
    AnalyzeAndPlanNode, ApplyChangesNode
from coding_agent.nodes.file_nodes import ReadFileAction, GrepSearchAction, \
    ListDirAction, DeleteFileAction
from coding_agent.nodes.response_nodes import FormatResponseNode

# Configure logging
logger = setup_logger("coding_agent")


def create_edit_flow() -> Flow:
    logger.info("Creating edit agent flow...")
    start = ReadTargetFileNode()
    start.to(AnalyzeAndPlanNode()).to(ApplyChangesNode())
    logger.info("Created edit agent flow!")
    return Flow(start=start)


def create_main_flow() -> Flow:
    logger.info("Creating main flow...")

    # Create nodes
    main_agent = MainDecisionAgent()
    read_action = ReadFileAction()
    grep_action = GrepSearchAction()
    list_dir_action = ListDirAction()
    delete_action = DeleteFileAction()
    edit_agent = create_edit_flow()
    format_response = FormatResponseNode()

    logger.info("Connecting main agent to action nodes...")
    # Connect main agent to action nodes
    main_agent.to(read_action, "read_file")
    main_agent.to(grep_action, "grep_search")
    main_agent.to(list_dir_action, "list_dir")
    main_agent.to(delete_action, "delete_file")
    main_agent.to(edit_agent, "edit_file")
    main_agent.to(format_response, "finish")

    logger.info("Connecting action nodes back to main agent...")
    # Connect action nodes back to main agent using default action
    read_action.to(main_agent)
    grep_action.to(main_agent)
    list_dir_action.to(main_agent)
    delete_action.to(main_agent)
    edit_agent.to(main_agent)

    logger.info("Created main flow!")
    return Flow(start=main_agent)


# Create the main flow
coding_agent_flow = create_main_flow()