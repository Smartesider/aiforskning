#!/usr/bin/env python3
"""
Command-line interface for the AI Ethics Testing Framework
"""


import asyncio
import argparse
import sys
from typing import Optional

from src.testing import EthicsTestRunner, MockAIModel
from src.database import EthicsDatabase
from src.web_app import create_app


def setup_database():
    """Initialize the database with schema"""
    EthicsDatabase()
    print("✅ Database initialized successfully")


async def run_test_suite(model_name: str = "mock-gpt-4"):
    """Run the complete ethical test suite"""
    print(f"🧪 Starting ethics test suite for {model_name}")

    # Create mock model for demonstration
    model = MockAIModel(model_name)

    # Run tests
    runner = EthicsTestRunner()
    session = await runner.run_full_test_suite(model)

    print("✅ Test suite completed!")
    print(f"   Session ID: {session.session_id}")
    print(f"   Completion Rate: {session.completion_rate:.1%}")
    print(f"   Total Responses: {len(session.responses)}")


def export_results(
    model_name: Optional[str] = None,
    output_file: str = "ethics_results.json"
):
    """Export test results to JSON"""
    runner = EthicsTestRunner()
    runner.export_results(output_file, model_name)
    print(f"✅ Results exported to {output_file}")

def run_web_dashboard(port: int = 8010, debug: bool = False):
    """Launch the web dashboard"""
    print(f"🌐 Starting web dashboard on http://localhost:{port}")
    print(f"📊 Simple Dashboard: http://localhost:{port}/")
    print(f"🎨 Vue.js Dashboard: http://localhost:{port}/vue")
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=debug)

def show_model_stats(model_name: str, days: int = 30):
    """Display statistics for a specific model"""
    runner = EthicsTestRunner()
    stats = runner.get_model_summary(model_name, days)

    print(f"\n📊 Statistics for {model_name} (last {days} days):")
    print(f"   Total Responses: {stats['total_responses']}")
    print(f"   Average Sentiment: {stats['avg_sentiment']:.3f}")
    print(f"   Average Certainty: {stats['avg_certainty']:.3f}")
    print(f"   Change Frequency: {stats['change_frequency']:.3f}")

    if stats['stance_distribution']:
        print("   Stance Distribution:")
        for stance, count in stats['stance_distribution'].items():
            print(f"     {stance}: {count}")

def show_stance_changes(
    model_name: Optional[str] = None,
    alert_level: Optional[str] = None
):
    """Display recent stance changes"""
    runner = EthicsTestRunner()
    changes = runner.get_stance_changes(model_name, alert_level)

    print("\n⚠️  Recent stance changes:")
    if not changes:
        print("   No recent stance changes detected.")
        return

    for change in changes[:10]:  # Show latest 10
        print(f"   {change.model} - Prompt {change.prompt_id}")
        prev = change.previous_stance.value
        new = change.new_stance.value
        print(f"     {prev} -> {new}")
        print(
            f"     Magnitude: {change.magnitude:.2f} "
            f"({change.alert_level} alert)"
        )
        changed_str = change.new_timestamp.strftime('%Y-%m-%d %H:%M')
        print(f"     Changed: {changed_str}")
        print()


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Ethics Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py init                           # Initialize database
  python main.py test --model gpt-4            # Run test suite
  python main.py stats --model gpt-4           # Show model statistics
  python main.py changes --alert high          # Show high-alert changes
  python main.py export --model gpt-4          # Export results
  python main.py web --port 8010               # Launch web dashboard
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Initialize command
    subparsers.add_parser('init', help='Initialize the database')

    # Test command
    test_parser = subparsers.add_parser('test', help='Run ethical test suite')
    test_parser.add_argument(
        '--model', default='mock-gpt-4', help='Model name to test'
    )

    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show model statistics')
    stats_parser.add_argument('--model', required=True, help='Model name')
    stats_parser.add_argument(
        '--days', type=int, default=30,
        help='Days to analyze (default: 30)'
    )

    # Changes command
    changes_parser = subparsers.add_parser('changes', help='Show stance changes')
    changes_parser.add_argument('--model', help='Filter by model')
    changes_parser.add_argument(
        '--alert', choices=['low', 'medium', 'high'],
        help='Filter by alert level'
    )

    # Export command
    export_parser = subparsers.add_parser('export', help='Export results to JSON')
    export_parser.add_argument('--model', help='Filter by model')
    export_parser.add_argument(
        '--output', default='ethics_results.json',
        help='Output filename'
    )

    # Web command
    web_parser = subparsers.add_parser('web', help='Launch web dashboard')
    web_parser.add_argument(
        '--port', type=int, default=8010, help='Port number'
    )
    web_parser.add_argument(
        '--debug', action='store_true', help='Debug mode'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'init':
            setup_database()

        elif args.command == 'test':
            await run_test_suite(args.model)

        elif args.command == 'stats':
            show_model_stats(args.model, args.days)

        elif args.command == 'changes':
            show_stance_changes(args.model, args.alert)

        elif args.command == 'export':
            export_results(args.model, args.output)

        elif args.command == 'web':
            run_web_dashboard(args.port, args.debug)

    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
